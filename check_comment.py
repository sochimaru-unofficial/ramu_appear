import os
import time
import requests

# 🔐 設定項目：すべてGitHubの金庫（シークレット環境変数）から自動で安全に読み込みます
VIDEO_URL = os.environ.get("VIDEO_URL")
TARGET_USER = os.environ.get("TARGET_USER")
API_KEY = os.environ.get("YOUTUBE_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

LAST_TIME_FILE = "last_comment_time.txt"

def get_last_check_time():
    if os.path.exists(LAST_TIME_FILE):
        with open(LAST_TIME_FILE, "r") as f:
            try:
                return float(f.read().strip())
            except ValueError:
                return 0.0
    return 0.0

def save_last_check_time(timestamp):
    with open(LAST_TIME_FILE, "w") as f:
        f.write(str(timestamp))

def send_discord_notification(author, message):
    payload = {
        "content": f"🔔 **【YouTube Live コメント通知】**\n**{author}** さんがコメントしました！\n💬 「{message}」"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def get_live_chat_id(video_id):
    # ✨ URLの組み立てを100%正しい形に一新しました
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "liveStreamingDetails",
        "id": video_id,
        "key": API_KEY
    }
    
    try:
        res = requests.get(url, params=params).json()
        return res["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
    except (KeyError, IndexError):
        # APIのエラーメッセージが返ってきた場合に原因が特定できるよう、ログに残します
        if "error" in res:
            print(f"⚠️ YouTube APIエラー: {res['error']['message']}", flush=True)
        return None

def main():
    print("【システム起動】監視を開始します...", flush=True)
    
    # 金庫の鍵が揃っているか超根本のチェック
    if not API_KEY or not DISCORD_WEBHOOK_URL or not VIDEO_URL or not TARGET_USER:
        print("❌ 必要なシークレット（金庫）が一部読み込めませんでした。GitHubのSettingsを確認してください。", flush=True)
        return
        
    chat_id = get_live_chat_id(VIDEO_URL)
    if not chat_id:
        print("❌ ライブチャットIDが取得できませんでした。まだ配信の待機画面が無いか、チャットが閉じられています。", flush=True)
        return
        
    last_check_time = get_last_check_time()
    new_last_time = last_check_time
    print(f"【ログ】前回のチェック基準時刻: {last_check_time}", flush=True)
    
    # 🔓 公式APIを使って安全に新着メッセージを取得します
    chat_url = "https://www.googleapis.com/youtube/v3/liveChat/messages"
    chat_params = {
        "liveChatId": chat_id,
        "part": "snippet,authorDetails",
        "key": API_KEY,
        "maxResults": 200
    }
    
    try:
        res = requests.get(chat_url, params=chat_params).json()
        items = res.get("items", [])
        print(f"【成功】公式API経由でチャットから新着コメントを検証中...（取得件数: {len(items)}件）", flush=True)
        
        for item in items:
            published_at = item["snippet"]["publishedAt"]
            # YouTubeの時刻データ（ISO形式）を比較可能な数値（タイムスタンプ）に変換
            time_struct = time.strptime(published_at.split(".")[0], "%Y-%m-%dT%H:%M:%S")
            current_timestamp = time.mktime(time_struct)
            
            # 前回の実行（5分前）よりも新しく書かれたコメントだけを処理
            if current_timestamp > last_check_time:
                author_name = item["authorDetails"]["displayName"]
                message_text = item["snippet"]["displayMessage"]
                
                # アカウント名が一致、またはお互いに含まれているか判定（部分一致）
                if TARGET_USER in author_name or author_name in TARGET_USER:
                    print(f"🎯 【判定一致！】{author_name}さんのコメント「{message_text}」を検知！", flush=True)
                    send_discord_notification(author_name, message_text)
                
                if current_timestamp > new_last_time:
                    new_last_time = current_timestamp
                    
    except Exception as e:
        print(f"❌ 処理中にエラーが発生しました: {e}", flush=True)
        return

    # 今回確認した一番新しいコメントの時刻をファイルに保存（次の5分後に引き継ぐ）
    save_last_check_time(new_last_time)
    print(f"【ログ】次回の基準時刻を更新しました: {new_last_time}", flush=True)

if __name__ == "__main__":
    main()
