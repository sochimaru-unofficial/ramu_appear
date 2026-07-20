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
    # 🧪 テスト用のダミーデータを作ります
    class DummyComment:
        def __init__(self, name, message, timestamp):
            self.author = type('Author', (object,), {'name': name})()
            self.message = message
            self.timestamp = timestamp
            self.datetime = "2026-07-20 00:00:00"

    # 1. あなたが設定したターゲット名を取得
    print(f"【テスト開始】設定されているターゲット名: {TARGET_USER}")
    
    # 2. 架空のコメント履歴を3つ用意します
    # （前回の時刻を 100.0 と仮定して、それより未来のタイムスタンプ 200.0 で検証します）
    last_check_time = 100.0 
    
    items = [
        DummyComment("一般の視聴者A", "こんにちは！", 200.0),
        DummyComment(TARGET_USER, "テストコメントです！届くかな？", 200.0), # 💡 ここで名前が一致するはず
        DummyComment("一般の視聴者B", "おつかれさまです", 200.0)
    ]

    print(f"【テスト】{len(items)}件のダミーコメントを読み込みました。検証を開始します。")
    
    for c in items:
        current_timestamp = c.timestamp / 1000.0  # ミリ秒変換のシミュレート
        current_timestamp = c.timestamp # テスト用にそのまま使用
        
        print(f" └ 確認中: [{c.author.name}]: {c.message}")
        
        if current_timestamp > last_check_time:
            # 設定した名前が含まれているかチェック
            if TARGET_USER in c.author.name:
                print(f"🎯 【判定一致！】{c.author.name}さんのコメントを検知しました！")
                
                # 実際にDiscordに送ってみる
                try:
                    send_discord_notification(c.author.name, c.message, c.datetime)
                    print("🚀 【Discord送信】成功しました！Discordを確認してください。")
                except Exception as discord_err:
                    print(f"❌ 【Discord送信エラー】Webhookの設定が違うかも: {discord_err}")

    print("【テスト終了】プログラムの判定チェックが完了しました。")
if __name__ == "__main__":
    main()
