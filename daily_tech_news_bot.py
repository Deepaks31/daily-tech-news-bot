import os
import requests
import html

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_tech_news():
    url = "https://hn.algolia.com/api/v1/search?tags=story&query=technology"
    res = requests.get(url).json()
    top_articles = res['hits'][:5]

    news = ""
    for a in top_articles:
        title = html.escape(a['title'])
        link = html.escape(a['url'])
        news += f"🔹 <b>{title}</b><br><a href=\"{link}\">{link}</a><br><br>"

    return f"📰 <b>Today's Tech News</b><br><br>{news}"

def send_to_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(telegram_url, data=data)
    print("Status:", response.status_code)
    print("Response:", response.text)

msg = get_tech_news()
send_to_telegram(msg)
