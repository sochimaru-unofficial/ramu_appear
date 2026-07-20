import os
import time
from datetime import datetime, timezone, timedelta
import requests
import json

# 🔐 設定項目
VIDEO_URL = os.environ.get("VIDEO_URL")
TARGET_USER = os.environ.get("TARGET_USER")
API_KEY = os.environ.get("YOUTUBE_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 管理するJSONファイル名
DATA_FILE = "comment_data.json"

# タイムゾーン設定 (JST)
JST = timezone(timedelta(hours=9))

def extract_video_id(url_or_id):
    """URLからビデオID（11桁）を自動抽出する関数"""
    if not url_or_id:
        return None
    if "v=" in url_or_id:
        return url_or_id.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url_or_id:
        return url_or_id.split("youtu.be/")[1].split("?")[0]
    return url_or_id

def load_comment_data():
    """JSONファイルからデータを読み込む。無い場合は初期値を返す"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass  # ファイルが破損していた場合は初期値へ
    
    # 初期データ構造
    return {
        "last_check_time": 0.0,
        "target_last_comment": {
            "time": "なし",
            "author": "なし",
            "message": "なし"
        }
    }

def save_comment_data(data):
    """データをJSONファイルに綺麗に保存する"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def send_discord_notification(author, message):
    payload = {
        "content": f"🔔 **【YouTube Live コメント通知】**\n**{author}** さんがコメントしました！\n💬 「{message}」"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ Discord通知の送信に失敗しました: {e}", flush=True)

def get_live_chat_id(video_id):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"part": "liveStreamingDetails", "id": video_id, "key": API_KEY}
    try:
        res = requests.get(url, params=params, timeout=10).json()
        return res["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
    except (KeyError, IndexError, requests.RequestException):
        return None

def main():
    print("【システム起動】監視を開始します...", flush=True)
    
    if not API_KEY or not DISCORD_WEBHOOK_URL or not VIDEO_URL or not TARGET_USER:
        print("❌ 必要なシークレット（金庫）が一部読み込めませんでした。", flush=True)
        return
        
    video_id = extract_video_id(VIDEO_URL)
    chat_id = get_live_chat_id(video_id)
    if not chat_id:
        print("❌ ライブチャットIDが取得できませんでした。配信が開始されていないか、URL/IDが間違っています。", flush=True)
        return
        
    # JSONから前回のデータを読み込み
    comment_data = load_comment_data()
    last_check_time = comment_data["last_check_time"]
    new_last_time = last_check_time
    
    chat_url = "https://www.googleapis.com/youtube/v3/liveChat/messages"
    chat_params = {
        "liveChatId": chat_id,
        "part": "snippet,authorDetails",
        "key": API_KEY,
        "maxResults": 200
    }
    
    try:
        res = requests.get(chat_url, params=chat_params, timeout=10).json()
        items = res.get("items", [])
        print(f"【成功】公式API経由でチャットから新着コメントを検証中...（取得件数: {len(items)}件）", flush=True)
        
for item in items:
            published_at = item["snippet"]["publishedAt"]  # 例: "2026-07-19T14:14:09.99687Z"
            
            # ✨【修正】ミリ秒の桁数が変則的でもエラーにならないよう、秒までを確実にパース
            time_str_seconds = published_at.split(".")[0]  # "2026-07-19T14:14:09" を抽出
            if time_str_seconds.endswith("Z"):             # ドットが無いケースの保険
                time_str_seconds = time_str_seconds[:-1]
            
            # UTC（世界標準時）として安全に datetime オブジェクトに変換
            dt_utc = datetime.strptime(time_str_seconds, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
            current_timestamp = dt_utc.timestamp()
            
            # ファイル保存用に正しい「日本時間」の文字列を作成
            dt_jst = dt_utc.astimezone(JST)
            jst_time_str = dt_jst.strftime("%Y-%m-%d %H:%M:%S")
            
            if current_timestamp > last_check_time:
                author_name = item["authorDetails"]["displayName"]
                message_text = item["snippet"]["displayMessage"]
                
                # ユーザー判定をご指定の元の形（部分一致）に戻しました！
                if TARGET_USER in author_name or author_name in TARGET_USER:
                    print(f"🎯 【判定一致！】ターゲットのコメントを検知！", flush=True)
                    send_discord_notification(author_name, message_text)
                    
                    # JSON内のターゲット発言情報を更新
                    comment_data["target_last_comment"] = {
                        "time": jst_time_str,
                        "author": author_name,
                        "message": message_text
                    }
                
                if current_timestamp > new_last_time:
                    new_last_time = current_timestamp
                    
    except Exception as e:
        print(f"❌ 処理中にエラーが発生しました: {e}", flush=True)
        return

    # 最新の基準時刻をデータにセットしてJSONに保存
    comment_data["last_check_time"] = new_last_time
    save_comment_data(comment_data)
    print(f"【ログ】データを更新して保存しました。次回の基準時刻: {new_last_time}", flush=True)

if __name__ == "__main__":
    main()
