import requests

def main():
    video_id = "Qk7-7AO_Z0Y" # 確認したい配信のID
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
    }
    
    print("【チェック開始】GitHubからYouTubeのページを読み込んでいます...")
    response = requests.get(url, headers=headers)
    html = response.text
    
    print(f"【チェック】通信ステータスコード: {response.status_code}")
    print("--------------------------------------------------")
    
    # 🕵️ YouTubeが送ってきたページに、Bot判定のキーワードが入っているか探します
    if "🤖" in html or "ロボット" in html or "Google" in html and "unusual traffic" in html or "captcha" in html.lower():
        print("❌ 【確定】YouTubeのBot検知（セキュリティ）に引っかかっています！")
        print("YouTubeから『普段と違うトラフィックが検出されました』というページを送りつけられています。")
    elif "ytInitialData" in html:
        print("⭕ 【セーフ】Botとしては弾かれていません！正常にページを読めています。")
        print("データ構造の解析部分（切り出し方）に問題があったようです。")
    else:
        print("❓ 【判定不能】Bot画面ではないですが、YouTubeの通常のページでもありません。")
        
    print("--------------------------------------------------")
    print("【参考】YouTubeから返ってきたページの冒頭1000文字:")
    print(html[:1000]) # 帰ってきたページの最初の部分をログに生表示します
