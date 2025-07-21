import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_tech_news():
    url = "https://hn.algolia.com/api/v1/search?tags=story&query=technology"
    res = requests.get(url).json()
    top_articles = res['hits'][:5]
    news = "\n\n".join([f"🔹 {a['title']}\n{a['url']}" for a in top_articles])
    return f"📰 *Today's Tech News*\n\n{news}"

def send_to_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(telegram_url, data=data)

msg = get_tech_news()
send_to_telegram(msg)
