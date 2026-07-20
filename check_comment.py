import requests
import sys

def main():
    video_id = "Qk7-7AO_Z0Y" # 確認したい配信のID
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
    }
    
    # sys.stdout.flush() を細かく入れて、文字を強制的に画面に引っ張り出します
    print("【チェック開始】GitHubからYouTubeのページを読み込んでいます...", flush=True)
    
    try:
        response = requests.get(url, headers=headers)
        html = response.text
    except Exception as e:
        print(f"❌ 通信自体に失敗しました: {e}", flush=True)
        return
    
    print(f"【チェック】通信ステータスコード: {response.status_code}", flush=True)
    print("--------------------------------------------------", flush=True)
    
    # YouTubeが送ってきたページに、Bot判定のキーワードが入っているか探します
    if "ロボット" in html or "Google" in html and "unusual traffic" in html or "captcha" in html.lower():
        print("❌ 【確定】YouTubeのBot検知（セキュリティ）に引っかかっています！", flush=True)
        print("YouTubeから『普段と違うトラフィックが検出されました』というページを送りつけられています。", flush=True)
    elif "ytInitialData" in html:
        print("⭕ 【セーフ】Botとしては弾かれていません！正常にページを読めています。", flush=True)
        print("データ構造の解析部分（切り出し方）に問題があったようです。", flush=True)
    else:
        print("❓ 【判定不能】Bot画面ではないですが、YouTubeの通常のページでもありません。", flush=True)
        
    print("--------------------------------------------------", flush=True)
    print("【参考】YouTubeから返ってきたページの冒頭1000文字:", flush=True)
    print(html[:1000], flush=True)
    print("\n【チェック完了】すべてのログを出力しました。", flush=True)

if __name__ == "__main__":
    main()
