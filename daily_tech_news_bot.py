import os
import requests
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Load Hugging Face summarization model (once)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# 1. Fetch news from NewsData.io
def get_tech_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&category=technology&language=en&country=us"
    response = requests.get(url)
    data = response.json()

    if "results" not in data or not data["results"]:
        return [{"title": "❌ No tech news found today.", "summary": ""}]

    articles = data["results"][:10]
    summarized_news = []

    for article in articles:
        title = (article.get("title") or "No title").strip()
        content = article.get("content") or article.get("description") or ""

        # Summarize using Hugging Face
        summary = summarize_with_hf(title + ". " + content)
        summarized_news.append({"title": title, "summary": summary})

    return summarized_news

# 2. Hugging Face summarization
def summarize_with_hf(text):
    try:
        if len(text) < 50:
            return "Too short to summarize."
        summary = summarizer(text, max_length=50, min_length=15, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"⚠️ Hugging Face summarization failed: {e}")
        return "Summary not available."

# 3. Send to Telegram
def send_to_telegram(summarized_news):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message = "📰 *Top Tech News Today*\n\n"

    for news in summarized_news:
        message += f"🔹 *{news['title']}*\n_{news['summary']}_\n\n"

    if len(message) > 4000:
        message = message[:4000] + "\n…"

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(telegram_url, data=data)
    print("✅ Telegram Status:", response.status_code)
    print("✅ Response:", response.text)

# ▶️ Run script
if __name__ == "__main__":
    news = get_tech_news()
    send_to_telegram(news)
