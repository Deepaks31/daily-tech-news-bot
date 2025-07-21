import os
import requests
from telegram import Bot

# Load secrets from environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

def fetch_top_tech_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&category=technology&language=en"
    try:
        response = requests.get(url)
        data = response.json()
        print("🔍 API Response:")
        print(data)
    except Exception as e:
        print("❌ Error fetching/parsing API:", e)
        return []

    if data.get("status") != "success":
        print("❌ API Error:", data.get("results", {}).get("message", "Unknown error"))
        return []

    articles = data.get("results")
    if not isinstance(articles, list):
        print("❌ No valid 'results' found.")
        return []

    return articles[:10]  # Get top 10

def format_news(news_list):
    formatted = "📰 *Top Tech News Today*\n\n"
    for idx, article in enumerate(news_list, 1):
        title = article.get("title", "No title")
        description = article.get("description", "").strip()
        link = article.get("link", "")
        pub_date = article.get("pubDate", "")
        formatted += (
            f"🔹 *{title}*\n"
            f"_{description}_\n"
            f"[Read more here]({link})\n"
            f"`Published: {pub_date}`\n\n"
        )
    return formatted

def send_telegram_message(message):
    bot = Bot(token=BOT_TOKEN)
    # Telegram message limit is ~4096 characters
    for i in range(0, len(message), 4000):
        bot.send_message(chat_id=CHAT_ID, text=message[i:i+4000], parse_mode="Markdown")

def main():
    news_list = fetch_top_tech_news()
    if not news_list:
        print("⚠️ No articles found or failed to fetch news.")
        return

    message = format_news(news_list)
    if message:
        send_telegram_message(message)
        print("✅ News sent successfully.")
    else:
        print("⚠️ No message content to send.")

if __name__ == "__main__":
    main()
