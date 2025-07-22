import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 1. Fetch news from NewsData.io (free plan)
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

        summary = summarize_with_gemini(title + "\n" + content)
        summarized_news.append({"title": title, "summary": summary})

    return summarized_news

# 2. Summarize using Gemini API from Google AI Studio (REST endpoint)
def summarize_with_gemini(content):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": f"Summarize this news in 1 or 2 lines:\n\n{content}"}]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"⚠️ Gemini summarization failed: {e}")
        return "Summary not available."

# 3. Send the summarized news to Telegram
def send_to_telegram(summarized_news):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message = "📰 *Top Tech News Today*\n\n"

    for news in summarized_news:
        message += f"🔹 *{news['title']}*\n_{news['summary']}_\n\n"

    # Telegram limit is ~4096 chars
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
