import os
import requests
import google.generativeai as genai

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def summarize_with_gemini(content):
    try:
        model = genai.GenerativeModel("gemini-pro")  # Use correct model ID
        response = model.generate_content(content)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Gemini summarization failed: {e}")
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
        description = (article.get("description") or "No description").strip()
        full_text = f"{title}\n\n{description}"
        summary = summarize_with_gemini(full_text)

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

# Run the bot
if __name__ == "__main__":
    messages = get_tech_news()
    send_to_telegram(messages)
