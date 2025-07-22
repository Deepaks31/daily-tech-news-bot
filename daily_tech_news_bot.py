import os
import requests

# ENV variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def summarize_with_gemini(text):
    gemini_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"Summarize the following news article in 2 lines:\n\n{text}"}]}]
    }

    try:
        response = requests.post(gemini_url, headers=headers, json=payload)
        response.raise_for_status()
        summary = response.json()['candidates'][0]['content']['parts'][0]['text']
        return summary
    except Exception as e:
        print("⚠️ Gemini summarization failed:", e)
        return "Summary not available."

def get_tech_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&category=technology&language=en&country=us"
    response = requests.get(url)
    data = response.json()

    if "results" not in data or not data["results"]:
        return ["❌ No tech news found today."]

    articles = data["results"][:10]
    news_messages = []
    current_message = "📰 Top Tech News Today\n\n"

    for i, article in enumerate(articles, 1):
        title = (article.get("title") or "No title").strip()
        content = (article.get("description") or title)
        summary = summarize_with_gemini(content)

        entry = f"🔹 {title}\n_{summary}_\n\n"
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
        print("✅ Telegram Status:", response.status_code)
        print("✅ Response:", response.text)

# Run
if __name__ == "__main__":
    messages = get_tech_news()
    send_to_telegram(messages)
