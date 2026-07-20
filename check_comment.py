import os
import sys

def main():
    print("【システム起動】金庫の受け渡し状態をチェックします...", flush=True)
    
    # 🕵️ 今、プログラムが認識できている環境変数の名前をすべてリストアップします
    available_keys = list(os.environ.keys())
    
    print("--------------------------------------------------", flush=True)
    print("【診断ログ】現在、プログラムに届いている設定一覧：", flush=True)
    for key in sorted(available_keys):
        # システム固有の細かい設定は除外し、私たちが設定したものに関わりそうなものだけ表示
        if "URL" in key or "KEY" in key or "USER" in key or "DISCORD" in key or "YOUTUBE" in key or "VIDEO" in key:
            # 安全のため、値そのものは絶対に表示せず、届いているか（True/False）だけを出します
            has_value = bool(os.environ.get(key))
            print(f" └ 📦 {key}: 届いていますか？ ➔ {has_value}", flush=True)
    print("--------------------------------------------------", flush=True)
    
    # ターゲットチェック
    video_url = os.environ.get("VIDEO_URL")
    target_user = os.environ.get("TARGET_USER")
    api_key = os.environ.get("YOUTUBE_API_KEY")
    discord_url = os.environ.get("DISCORD_WEBHOOK_URL")
    
    missing = []
    if not discord_url: missing.append("DISCORD_WEBHOOK_URL")
    if not api_key: missing.append("YOUTUBE_API_KEY")
    if not video_url: missing.append("VIDEO_URL")
    if not target_user: missing.append("TARGET_USER")
    
    if missing:
        print(f"❌ 判定：プログラムが以下の情報を読み込めませんでした: {', '.join(missing)}", flush=True)
        print("💡 対策：これが届いていないということは、check.yml の『env:』の書き方にズレがある可能性が高いです。", flush=True)
    else:
        print("⭕ 判定：すべてのシークレットが正常にプログラムに届いています！", flush=True)
        print("（もしこれが⭕なら、次のステップで自動的に通信を開始させます）", flush=True)

if __name__ == "__main__":
    main()
