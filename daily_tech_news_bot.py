import os
import requests
from transformers import pipeline

# Environment variables (from GitHub secrets or local .env)
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
NEWSDATA_API_KEY = os.getenv("NEWS_API_KEY")

NEWS_API_URL = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&category=technology&language=en"

# Load summarization pipeline
print("Loading summarizer...")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
print("Device set to use", summarizer.device)

def get_tech_news():
    try:
        response = requests.get(NEWS_API_URL)
        data = response.json()
        results = data.get("results", [])
        if isinstance(results, list):
            return results[:10]  # top 10 articles
        else:
            print("Unexpected results format:", type(results))
            return []
    except Exception as e:
        print("Error fetching news:", e)
        return []

def summarize_text(text, max_tokens=130):
    if not text or len(text.split()) < 50:
        return text  # Skip summarizing short texts
    try:
        summary = summarizer(text, max_length=max_tokens, min_length=25, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print("Error summarizing:", e)
        return text

def send_news_to_telegram():
    articles = get_tech_news()
    if not articles:
        print("No articles found.")
        return

    message = "📰 *Top Tech News Today*\n\n"
    for article in articles:
        title = article.get("title", "No Title")
        desc = article.get("description") or article.get("content") or ""
        summary = summarize_text(desc)
        message += f"🔹 *{title}*\n_{summary}_\n\n"

    # Send to Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    res = requests.post(url, data=payload)
    print("Telegram send status:", res.status_code)

if __name__ == "__main__":
    send_news_to_telegram()
