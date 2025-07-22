import requests
import datetime
import os
from google.generativeai import configure, GenerativeModel

# Configurations
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

configure(api_key=GEMINI_API_KEY)
model = GenerativeModel("gemini-pro")

NEWS_API_URL = (
    f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&language=en&category=technology&country=us,in&size=10"
)

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def summarize_with_gemini(text):
    if not text or len(text.strip()) < 30:
        return "⚠️ Not enough content to summarize."
    try:
        response = model.generate_content(
            f"Summarize this tech news article in 2 lines:
\n{text}",
            generation_config={"temperature": 0.5}
        )
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Gemini failed to summarize: {e}"


def get_tech_news():
    try:
        res = requests.get(NEWS_API_URL)
        data = res.json()
        articles = data.get("results", [])

        message = "\U0001F4F0 *Top Tech News (Summarized)*\n\n"
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            content = article.get("content") or article.get("description") or ""
            summary = summarize_with_gemini(content)

            message += f"\u25B6️ *{title}*\n_{summary}_\n\n"

        return message.strip()
    except Exception as e:
        return f"⚠️ Failed to fetch news: {e}"


def send_to_telegram(message):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    res = requests.post(TELEGRAM_URL, json=payload)
    print("Status:", res.status_code)
    print("Response:", res.text)


if __name__ == "__main__":
    news_message = get_tech_news()
    send_to_telegram(news_message)
