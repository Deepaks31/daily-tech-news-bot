import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

TEXT = "Daily Tech Update: OpenAI releases GPT-4.5 Turbo!"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {
    "chat_id": CHAT_ID,
    "text": TEXT
}

response = requests.post(url, data=data)
print("Status Code:", response.status_code)
print("Response:", response.text)
