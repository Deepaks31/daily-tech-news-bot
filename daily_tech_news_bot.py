import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_tech_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&category=technology&language=en&country=us"
    response = requests.get(url)
    data = response.json()

    if "results" not in data or not data["results"]:
        return "❌ No articles found today."

    articles = data["results"][:10]
    news = ""
    for i, article in enumerate(articles, 1):
        title = article.get("title", "No title")
        description = article.get("description", "No description")
        news += f"🔹 *{title}*\n_{description}_\n\n"

    return f"📰 *Top 10 Tech News Today*\n\n{news}"

def send_to_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(telegram_url, data=data)
    print("Status:", response.status_code)
    print("Response:", response.text)

# Run the bot
message = get_tech_news()
send_to_telegram(message)
