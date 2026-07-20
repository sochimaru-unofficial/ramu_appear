import os
import time
import requests

# 🔐 設定項目
VIDEO_URL = os.environ.get("VIDEO_URL")
TARGET_USER = os.environ.get("TARGET_USER")
API_KEY = os.environ.get("YOUTUBE_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

LAST_TIME_FILE = "last_comment_time.txt"
TARGET_COMMENT_FILE = "target_last_comment.txt" # ✨ ターゲット専用の保存ファイル

def get_last_check_time():
    if os.path.exists(LAST_TIME_FILE):
        with open(LAST_TIME_FILE, "r") as f:
            try: return float(f.read().strip())
            except ValueError: return 0.0
    return 0.0

def save_last_check_time(timestamp):
    with open(LAST_TIME_FILE, "w") as f:
        f.write(str(timestamp))

# ✨ ターゲットの最新コメント履歴を読み込む関数
def print_target_last_comment():
    if os.path.exists(TARGET_COMMENT_FILE):
        with open(TARGET_COMMENT_FILE, "r", encoding="utf-8") as f:
            print(f"📌 【ターゲットの直近の記録】\n{f.read()}", flush=True)
    else:
        print("📌 【ターゲットの直近の記録】まだこのシステムで検知したコメントはありません。", flush=True)

# ✨ ターゲットの最新コメント履歴を保存する関数
def save_target_last_comment(author, message, jst_time_str):
    with open(TARGET_COMMENT_FILE, "w", encoding="utf-8") as f:
        f.write(f"時刻: {jst_time_str}\n発言: {message}")

def send_discord_notification(author, message):
    payload = {
        "content": f"🔔 **【YouTube Live コメント通知】**\n**{author}** さんがコメントしました！\n💬 「{message}」"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def get_live_chat_id(video_id):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"part": "liveStreamingDetails", "id": video_id, "key": API_KEY}
    try:
        res = requests.get(url, params=params).json()
        return res["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
    except (KeyError, IndexError):
        return None

def main():
    print("【システム起動】監視を開始します...", flush=True)
    
    if not API_KEY or not DISCORD_WEBHOOK_URL or not VIDEO_URL or not TARGET_USER:
        print("❌ 必要なシークレット（金庫）が一部読み込めませんでした。", flush=True)
        return
        
    chat_id = get_live_chat_id(VIDEO_URL)
    if not chat_id:
        print("❌ ライブチャットIDが取得できませんでした。", flush=True)
        return
        
    # ✨ 起動時に、前回収穫した推しのコメントをログに表示！
    print_target_last_comment()
    print("--------------------------------------------------", flush=True)
    
    last_check_time = get_last_check_time()
    new_last_time = last_check_time
    
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
            time_struct = time.strptime(published_at.split(".")[0], "%Y-%m-%dT%H:%M:%S")
            current_timestamp = time.mktime(time_struct)
            
            # 日本時間に変換した文字列を作る（ログ・ファイル保存用）
            jst_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_timestamp))
            
            if current_timestamp > last_check_time:
                author_name = item["authorDetails"]["displayName"]
                message_text = item["snippet"]["displayMessage"]
                
                if TARGET_USER in author_name or author_name in TARGET_USER:
                    print(f"🎯 【判定一致！】{author_name}さんのコメント「{message_text}」を検知！", flush=True)
                    send_discord_notification(author_name, message_text)
                    
                    # ✨ 推しが発言したら、その内容と時間をファイルに上書き保存！
                    save_target_last_comment(author_name, message_text, jst_time_str)
                
                if current_timestamp > new_last_time:
                    new_last_time = current_timestamp
                    
    except Exception as e:
        print(f"❌ 処理中にエラーが発生しました: {e}", flush=True)
        return

    save_last_check_time(new_last_time)
    print(f"【ログ】次回の基準時刻を更新しました: {new_last_time}", flush=True)

if __name__ == "__main__":
    main()
