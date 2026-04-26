"""
Start the LINE bot with a public ngrok tunnel.

Steps before running:
  1. Fill in .env (LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN,
                   ANTHROPIC_API_KEY, NGROK_AUTHTOKEN)
  2. python start.py
  3. Copy the printed Webhook URL into LINE Developers console
     Messaging API > Webhook settings > Webhook URL
     Then click "Verify" and enable "Use webhook"
"""
import os
import threading
from dotenv import load_dotenv

load_dotenv()

from pyngrok import ngrok, conf
from bot.line_bot import app

PORT = 5000


def _start_flask():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


def main():
    authtoken = os.environ.get("NGROK_AUTHTOKEN", "").strip()
    if not authtoken or authtoken == "your_ngrok_authtoken_here":
        print("[!] NGROK_AUTHTOKEN not set in .env — tunnel may be limited or fail.")
    else:
        conf.get_default().auth_token = authtoken

    for key in ("LINE_CHANNEL_SECRET", "LINE_CHANNEL_ACCESS_TOKEN", "ANTHROPIC_API_KEY"):
        val = os.environ.get(key, "")
        if not val or val.startswith("your_"):
            raise SystemExit(f"[!] {key} is not set in .env — please fill it in first.")

    tunnel = ngrok.connect(PORT, "http")
    public_url = tunnel.public_url.replace("http://", "https://")
    webhook_url = f"{public_url}/callback"

    print("=" * 60)
    print(f"  Webhook URL:  {webhook_url}")
    print("=" * 60)
    print("  Paste this URL into LINE Developers console:")
    print("  Messaging API > Webhook settings > Webhook URL")
    print("  Then click Verify and turn on 'Use webhook'")
    print("=" * 60)
    print("  Bot is running. Press Ctrl+C to stop.\n")

    flask_thread = threading.Thread(target=_start_flask, daemon=True)
    flask_thread.start()

    try:
        flask_thread.join()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        ngrok.kill()


if __name__ == "__main__":
    main()
