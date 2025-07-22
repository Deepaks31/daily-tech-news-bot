import os
import requests
import google.generativeai as genai

# Load secrets from GitHub Actions environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

def summarize_with_gemini(text):
    try:
        response = model.generate_content(f"Summarize the following news in 2-3 lines:\n{text}")
        return response.text.strip()
    except Exception as e:
        return "⚠️ Gemini failed to summarize."

def get_tech_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&category=technology&language=en&country=us"
    response = requests.get(url)
    data = response.json()

    if "results" not in data or not data["results"]:
        return ["❌ No tech news found today."]

    articles = data["results"][:5]
    news_messages = []
    message = "📰 *Top Tech News (Summarized)*\n\n"

    for i, article in enumerate(articles, 1):
        title = article.get("title", "No title")
        content = article.get("description") or article.get("content") or ""
        summary = summarize_with_gemini(content)

        entry = f"🔹 *{title}*\n_{summary}_\n\n"
        if len(message) + len(entry) > 3900:
            news_messages.append(message)
            message = ""
        message += entry

    if message:
        news_messages.append(message)

    return news_messages

def send_to_telegram(messages):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for message in messages:
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        res = requests.post(telegram_url, data=payload)
        print("Status:", res.status_code)
        print("Response:", res.text)

# Run the bot
if __name__ == "__main__":
    messages = get_tech_news()
    send_to_telegram(messages)
