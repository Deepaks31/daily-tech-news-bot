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
        print("❌ Failed to parse JSON:", e)
        print("🔍 Raw response:", response.text)
        return ["❌ Failed to fetch or parse tech news."]

    if data.get("status") != "success":
        print("❌ API Error:", data.get("results", {}).get("message", "Unknown error"))
        print("🔍 Full API response:", data)
        return ["❌ API Error: " + data.get("results", {}).get("message", "Unknown error")]

    articles = data.get("results")
    if not articles:
        return ["⚠️ No articles found or failed to fetch news."]

    news_messages = []
    current_message = "📰 *Top Tech News Today*\n\n"

    for i, article in enumerate(articles[:10], 1):
        title = article.get("title", "No title").replace('*', '').replace('_', '')
        description = article.get("description", "No description").replace('*', '').replace('_', '')

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
        print("✅ Status:", response.status_code)
        print("📨 Response:", response.text)

if __name__ == "__main__":
    messages = get_tech_news()
    send_to_telegram(messages)
