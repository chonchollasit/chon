"""
Start the LINE bot with a public localtunnel tunnel.

Steps before running:
  1. Fill in .env (LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN,
                   ANTHROPIC_API_KEY)
  2. python start.py
  3. Copy the printed Webhook URL into LINE Developers console
     Messaging API > Webhook settings > Webhook URL
     Then click "Verify" and enable "Use webhook"
"""
import os
import re
import subprocess
import threading
import time
from dotenv import load_dotenv

load_dotenv()

PORT = 5000


def _start_flask():
    from bot.line_bot import app
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


def _start_tunnel():
    proc = subprocess.Popen(
        ["lt", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in proc.stdout:
        line = line.strip()
        match = re.search(r"https://[^\s]+", line)
        if match:
            return match.group(0), proc
    raise RuntimeError("localtunnel did not return a URL")


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
    time.sleep(1)

    try:
        public_url, tunnel_proc = _start_tunnel()
        _print_webhook(public_url)
        flask_thread.join()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        try:
            tunnel_proc.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    main()
