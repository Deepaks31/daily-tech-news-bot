import os
import requests
import google.generativeai as genai
from datetime import datetime

# Load environment variables
NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # NewsData.io key
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")


def get_tech_news():
    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": NEWS_API_KEY,
        "q": "technology",  # Use general query
        "page": 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        articles = data.get("results", [])
        if not articles:
            print("⚠️ No articles found in API response.")
        return articles[:10]
    except requests.exceptions.HTTPError as err:
        print(f"❌ Failed to fetch news: {err}")
        return []


def summarize_article(content):
    try:
        prompt = f"Summarize this tech news article in 2 lines:\n{content}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Gemini error: {e}")
        return "⚠️ Gemini failed to summarize."


def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print(f"✅ Telegram Status: {response.status_code}")
    print(response.text)


def main():
    news_items = get_tech_news()
    if not news_items:
        send_to_telegram("⚠️ No tech news found today.")
        return

    summary_lines = [f"📰 *Top Tech News - {datetime.now().strftime('%d %b %Y')}*\n"]

    for item in news_items:
        title = item.get("title", "No Title")
        content = item.get("content") or item.get("description") or item.get("link", "")
        summary = summarize_article(content)
        summary_lines.append(f"🔹 *{title}*\n{summary}\n")

    final_message = "\n".join(summary_lines)
    send_to_telegram(final_message)


if __name__ == "__main__":
    main()
