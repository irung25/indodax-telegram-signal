import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("BOT_TOKEN ADA:", BOT_TOKEN is not None)
print("CHAT_ID ADA:", CHAT_ID is not None)

if not BOT_TOKEN or not CHAT_ID:
    print("❌ ENV BELUM TERBACA")
    exit()

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": "✅ TEST BOT: Telegram sudah terhubung"
}

response = requests.post(url, data=payload)

print("STATUS CODE:", response.status_code)
print("RESPONSE:", response.text)
