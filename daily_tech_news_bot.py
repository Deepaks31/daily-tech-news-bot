import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_tech_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&category=technology&language=en&country=us"
    response = requests.get(url)
    try:
        data = response.json()
    except Exception as e:
        return [f"❌ Failed to parse JSON: {str(e)}"]

    if not isinstance(data.get("results"), list):
        return [f"❌ Unexpected API response: {data}"]

    articles = data["results"][:10]
    news_messages = []
    current_message = "📰 *Top Tech News Today*\n\n"

    for i, article in enumerate(articles, 1):
        title = article.get("title", "No title").strip()
        description = article.get("description", "No description").strip()
        entry = f"🔹 *{title}*\n_{description}_\n\n"

        if len(current_message) + len(entry) > 3900:
            news_messages.append(current_message)
            current_message = ""

        current_message += entry

    if current_message:
        news_messages.append(current_message)

    return news_messages

def send_to_telegram(messages):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for message in messages:
        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(telegram_url, data=data)
        print("Status:", response.status_code)
        print("Response:", response.text)

# Run
messages = get_tech_news()
send_to_telegram(messages)


