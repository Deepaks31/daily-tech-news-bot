import os
import requests
from transformers import pipeline
import torch

# Load secrets from environment (GitHub Secrets recommended)
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Set device to CPU
device = 0 if torch.cuda.is_available() else -1
print("Device set to use", "GPU" if device == 0 else "CPU")

# Load summarizer
print("Loading summarizer...")
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small", device=device)

# Get tech news from NewsData.io
def get_tech_news():
    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": NEWS_API_KEY,
        "q": "technology",
        "language": "en",
        "page": 1
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        return data.get("results", [])
    except Exception as e:
        print("Error fetching news:", e)
        return []

# Format and summarize for Telegram
def format_news(news_list):
    message = "📢 *Top Tech News Today*\n\n"
    for article in news_list[:10]:  # Limit to 10 articles
        title = article.get("title", "No Title").strip()
        content = article.get("content") or article.get("description") or title
        try:
            summary = summarizer(content[:512], max_length=35, min_length=10, do_sample=False)[0]['summary_text']
        except:
            summary = content[:100] + "..."
        message += f"📰 *{title}*\n{summary.strip()}\n\n"
    if len(message) > 4000:
        message = message[:4000] + "\n\n[...truncated]"
    return message

# Send message to Telegram
def send_to_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    res = requests.post(url, json=payload)
    print("✅ Telegram Status:", res.status_code)
    if res.status_code != 200:
        print("❌ Error Response:", res.text)

# Main function
def main():
    articles = get_tech_news()
    if not articles:
        print("No articles found.")
        return
    message = format_news(articles)
    send_to_telegram(message)

if __name__ == "__main__":
    main()
