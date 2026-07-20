import os
import time
import pytchat
import requests

# ---------------- 設定項目 ----------------
VIDEO_URL = "Qk7-7AO_Z0Y"                       # 監視したい配信のID
TARGET_USER = "@O_Ramu_oo"                     # 探したい人の正確な名前
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
# ------------------------------------------

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

def send_discord_notification(author, message, datetime_str):
    payload = {
        "content": f"🔔 **【YouTube Live コメント通知】**\n**{author}** さんがコメントしました！\n💬 「{message}」\n🕒 {datetime_str}"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def main():
    last_check_time = get_last_check_time()
    new_last_time = last_check_time
    
    print(f"【ログ】前回のチェック基準時刻: {last_check_time}")
    
    try:
        chat = pytchat.create(video_id=VIDEO_URL)
        
        # ✨ 改善ポイント：空振りを防ぐため、最大5回（約5秒間）データが取れるまでリトライする
        retry_count = 0
        items = []
        while chat.is_alive() and retry_count < 5:
            items = chat.get().sync_items()
            if items: # データが取れたらループを抜ける
                break
            print("【ログ】チャットデータがまだ空のため、1秒待機して再取得します...")
            time.sleep(1)
            retry_count += 1
            
        if not items:
            print("【ログ】チャットデータが取得できませんでした（新着なし、または待機中による制限）。処理を終了します。")
            return

        # 取得できたコメントを精査
        print(f"【ログ】{len(items)}件のコメントを読み込みました。検証を開始します。")
        for c in items:
            current_timestamp = c.timestamp / 1000.0
            
            # どんなコメントが流れているかログに表示（原因特定用）
            print(f" └ 確認中: [{c.author.name}]: {c.message}")
            
            if current_timestamp > last_check_time:
                # ターゲット名が含まれているか判定
                if TARGET_USER in c.author.name:
                    print(f"🎯 【発見】{c.author.name}さんのコメントを検知しました！")
                    send_discord_notification(c.author.name, c.message, c.datetime)
                
                if current_timestamp > new_last_time:
                    new_last_time = current_timestamp
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return

    save_last_check_time(new_last_time)
    print(f"【ログ】次回の基準時刻を更新しました: {new_last_time}")

if __name__ == "__main__":
    main()
