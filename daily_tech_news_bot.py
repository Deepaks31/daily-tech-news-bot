import os
import requests
from transformers import pipeline

# --- Load from environment variables ---
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
NEWSDATA_API_KEY = os.getenv("NEWS_API_KEY")

NEWS_API_URL = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&category=technology&language=en"

# Hugging Face Summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def get_tech_news():
    try:
        response = requests.get(NEWS_API_URL)
        articles = response.json().get("results", [])[:10]
        return articles
    except Exception as e:
        print("Error fetching news:", e)
        return []

def summarize_text(text, max_tokens=130):
    if len(text.split()) < 50:
        return text
    summary = summarizer(text, max_length=max_tokens, min_length=25, do_sample=False)
    return summary[0]['summary_text']

def send_news_to_telegram():
    articles = get_tech_news()
    if not articles:
        return

    message = "📰 *Top Tech News Today*\n\n"
    for article in articles:
        title = article.get("title", "No Title")
        desc = article.get("description", "") or article.get("content", "")
        summary = summarize_text(desc)
        message += f"🔹 *{title}*\n_{summary}_\n\n"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    send_news_to_telegram()
