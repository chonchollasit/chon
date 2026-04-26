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

PORT = 5000


def _start_flask():
    from bot.line_bot import app
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


def _start_ngrok():
    from pyngrok import ngrok, conf
    authtoken = os.environ.get("NGROK_AUTHTOKEN", "").strip()
    if authtoken and not authtoken.startswith("your_"):
        conf.get_default().auth_token = authtoken
    tunnel = ngrok.connect(PORT, "http")
    return tunnel.public_url.replace("http://", "https://")


def _print_webhook(url: str):
    print("=" * 60)
    print(f"  Webhook URL:  {url}/callback")
    print("=" * 60)
    print("  Paste into LINE Developers console:")
    print("  Messaging API > Webhook settings > Webhook URL")
    print("  Click Verify then turn on 'Use webhook'")
    print("=" * 60)
    print("  Bot is running. Press Ctrl+C to stop.\n")


def main():
    for key in ("LINE_CHANNEL_SECRET", "LINE_CHANNEL_ACCESS_TOKEN"):
        val = os.environ.get(key, "")
        if not val or val.startswith("your_"):
            raise SystemExit(f"[!] {key} is not set in .env")

    flask_thread = threading.Thread(target=_start_flask, daemon=True)
    flask_thread.start()

    try:
        public_url = _start_ngrok()
        _print_webhook(public_url)
    except Exception as e:
        print(f"[!] ngrok failed: {e}")
        print(f"[!] Flask is running on port {PORT}.")
        print(f"[!] Expose it manually (ngrok desktop app, cloudflared, etc.)")
        print(f"[!] Then set webhook to: https://<your-url>/callback\n")

    try:
        flask_thread.join()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        try:
            from pyngrok import ngrok
            ngrok.kill()
        except Exception:
            pass


if __name__ == "__main__":
    main()
