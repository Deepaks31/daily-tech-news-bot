import os
import requests
import google.generativeai as genai
from datetime import datetime

# Load environment variables
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
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
        "category": "technology",
        "language": "en",
        "country": "us,in,gb",
        "page": 1
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("results", [])[:10]


def summarize_article(content):
    try:
        prompt = (
            "Summarize this tech news article in 2 lines:\n" + content
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "⚠️ Gemini failed to summarize."


def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}\nResponse: {response.text}")


def main():
    news_items = get_tech_news()
    summary_lines = ["📰 *Top Tech News (Summarized)*\n"]

    for item in news_items:
        title = item.get("title", "No Title")
        content = item.get("content") or item.get("description") or item.get("link", "")
        summary = summarize_article(content)
        summary_lines.append(f"🔹 *{title}*\n{summary}\n")

    full_message = "\n".join(summary_lines)
    send_to_telegram(full_message)


if __name__ == "__main__":
    main()
