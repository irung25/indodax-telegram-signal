import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_test_message():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "✅ Bot Indodax Signal AKTIF & SIAP!"
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    send_test_message()
