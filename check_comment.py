import os
import time
import pytchat
import requests

# ---------------- 設定項目 ----------------
VIDEO_URL = "https://www.youtube.com/live/Qk7-7AO_Z0Y" # 監視したい配信のURL
TARGET_USER = "@O_Ramu_oo" # 探したい人の正確な名前
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1528391991485010111/my2lmN_LjX5x7fFxehOlCXHtjX9FQBEawrkT3Lt8cq42PgAd9BcRkyaqnQ2R1PnvAV0n" # DiscordのWebhook URL
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
    
    try:
        # pytchatで最新のチャットを取得
        chat = pytchat.create(video_id=VIDEO_URL)
        
        # 配信中の全チャットを一通り走査（最新のものまで追いつく）
        while chat.is_alive():
            for c in chat.get().sync_items():
                # タイムスタンプを取得（ミリ秒を秒に変換）
                current_timestamp = c.timestamp / 1000.0
                
                # 前回のチェックより新しいコメント、かつターゲットのユーザーの場合
                if current_timestamp > last_check_time:
                    if c.author.name == TARGET_USER:
                        print(f"発見: {c.message}")
                        send_discord_notification(c.author.name, c.message, c.datetime)
                    
                    # 最後に確認したタイムスタンプを更新
                    if current_timestamp > new_last_time:
                        new_last_time = current_timestamp
            
            # 一度最新まで追いついたらループを抜ける
            break
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return

    # 最新のチェック時刻を保存
    save_last_check_time(new_last_time)

if __name__ == "__main__":
    main()
