import os
import sys
import json
import re
import requests

# ---------------- 設定項目 ----------------
VIDEO_URL = "Qk7-7AO_Z0Y"                           # 監視したい配信のID（ログにあったもの）
TARGET_USER = "@O_Ramu_oo"                         # 探したい人の正確なアカウント名
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
# ------------------------------------------

def send_discord_notification(author, message):
    payload = {
        "content": f"🔔 **【YouTube Live 実機テスト成功！】**\n本物のチャットから検知しました！\n👤 **{author}** さん\n💬 「{message}」"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def get_live_html(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    return response.text

def main():
    print(f"【実機テスト開始】設定されているターゲット名: {TARGET_USER}")
    print(f"【実機テスト】配信ID: {VIDEO_URL} の最新チャットを解析中...")
    
    html = get_live_html(VIDEO_URL)
    
    # YouTubeの画面データからチャットの生データ（JSON）を力技で抽出します
    raw_data = re.search(r'ytInitialData\s*=\s*({.+?});', html)
    if not raw_data:
        print("❌ YouTubeのデータ構造の抽出に失敗しました。配信URLが間違っているか、ページ構成が変わっています。")
        return
        
    try:
        json_data = json.loads(raw_data.group(1))
        # 待機画面のチャットデータが入っている深い階層を掘り進みます
        actions = json_data["contents"]["twoColumnWatchNextResults"]["conversationBar"]["liveChatRenderer"]["actions"]
    except KeyError:
        print("❌ チャットデータが見つかりませんでした。まだ誰もコメントしていないか、チャット欄が閉じられています。")
        return

    # 一番最後（最新）のコメントを1件だけ取得
    latest_action = actions[-1]
    try:
        item = latest_action["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]
        author_name = item["authorName"]["simpleText"]
        
        # メッセージテキストの組み立て
        message_runs = item["message"]["runs"]
        message_text = "".join([run.get("text", "") for run in message_runs])
        
        print(f"【取得成功】現在のチャット欄の最新コメント:")
        print(f" └ [投稿者]: {author_name}")
        print(f" └ [内 容]: {message_text}")
        
        # ターゲットの名前と一致するかチェック（部分一致）
        if TARGET_USER in author_name:
            print(f"🎯 【判定一致！！】ターゲットの最新コメントを検知しました！")
            send_discord_notification(author_name, message_text)
            print("🚀 Discordに本物の最新コメントを転送しました！確認してください。")
        else:
            print(f"⏭️ 判定不一致: 最新のコメントは別の人（{author_name}さん）のものでした。")
            print(f"💡 ヒント: お目当ての「{TARGET_USER}」さんに、いまチャット欄へ新しく何かコメントを書き込んでもらってから、もう一度実行すると判定が一致します！")

    except KeyError:
        print("⚠️ 最新のデータが通常のテキストコメントではありませんでした（スタンプやスーパーチャットなど）。もう一度実行してみてください。")

if __name__ == "__main__":
    main()
