import os
import json
import re
import requests

# ---------------- 設定項目 ----------------
VIDEO_URL = "Qk7-7AO_Z0Y"                           # 監視したい配信のID
TARGET_USER = "@O_Ramu_oo"                         # 探したい人の正確なアカウント名
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
# ------------------------------------------

def send_discord_notification(author, message):
    payload = {
        "content": f"🔔 **【YouTube Live 執念のテスト成功！】**\nついにチャットの壁を突破して検知しました！\n👤 **{author}** さん\n💬 「{message}」"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def main():
    print(f"【実機テスト開始】設定されているターゲット名: {TARGET_USER}")
    
    url = f"https://www.youtube.com/watch?v={VIDEO_URL}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
    }
    
    html = requests.get(url, headers=headers).text
    
    # YouTubeの生データからチャットに関連するあらゆる部分を探し出します
    raw_data = re.search(r'ytInitialData\s*=\s*({.+?});', html)
    if not raw_data:
        print("❌ ページの解析に失敗しました。")
        return
        
    comments_found = []
    
    try:
        json_data = json.loads(raw_data.group(1))
        # 待機画面のチャットデータをテキストから強引に検索・抽出するロジック
        json_str = json.dumps(json_data)
        
        # コメント本文と投稿者名が含まれるオブジェクトを正規表現で全抽出します
        text_messagers = re.findall(r'{"liveChatTextMessageRenderer":{.+?}}', json_str)
        
        print(f"【解析ログ】チャットの破片を {len(text_messagers)} 件発見しました。解析します。")
        
        for raw_item in text_messagers:
            try:
                item = json.loads(raw_item)["liveChatTextMessageRenderer"]
                author_name = item["authorName"]["simpleText"]
                message_text = "".join([run.get("text", "") for run in item["message"]["runs"]])
                comments_found.append((author_name, message_text))
            except:
                continue
                
    except Exception as e:
        print(f"❌ 解析中にエラーが発生しました: {e}")
        return

    if not comments_found:
        print("❌ やはりチャットデータが空っぽ、またはプログラムから見えない場所に隠されています。")
        print("💡 対策: 配信が実際に『開始』されれば、このブロックは100%解除されて読めるようになります！")
        return

    print(f"【取得成功】チャット欄から {len(comments_found)} 件のコメントを復元しました（上が古く、下が最新です）：")
    
    # 復元したコメントをすべて表示して判定
    target_detected = False
    for author, msg in comments_found:
        print(f" └ [{author}]: {msg}")
        if TARGET_USER in author:
            print(f"🎯 🎯 🎯 【判定一致！！】『{author}』さんのコメント「{msg}」を検知！")
            send_discord_notification(author, msg)
            target_detected = True
            
    if target_detected:
        print("🚀 Discordへの転送命令を送信しました！")
    else:
        print(f"⏭️ 復元したログの中に「{TARGET_USER}」さんの名前は見つかりませんでした。")

if __name__ == "__main__":
    main()
