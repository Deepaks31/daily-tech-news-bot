import os
import requests
import google.generativeai as genai

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Setup Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

def get_tech_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q=technology"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("❌ Failed to fetch news:", e)
        return ["❌ Error fetching news from NewsData.io."]

    if "results" not in data or not data["results"]:
        return ["❌ No tech news found today."]

    return data["results"][:10]  # Top 10 articles

def summarize_with_gemini(content):
    try:
        model = genai.GenerativeModel("gemini-pro")  # ✅ Correct model ID for v1
        response = model.generate_content(content)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Gemini summarization failed: {e}")
        return "Summary not available."

def format_messages(articles):
    news_messages = []
    current_message = "📰 *Top Tech News Today*\n\n"

    for article in articles:
        title = (article.get("title") or "No Title").strip()
        content = (
            article.get("content") or
            article.get("description") or
            article.get("title") or
            "No content available."
        ).strip()

        summary = summarize_content(content)
        entry = f"🔹 *{title}*\n_{summary}_\n\n"

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

# Run everything
articles = get_tech_news()
if isinstance(articles, list) and isinstance(articles[0], str):
    send_to_telegram(articles)  # It's an error or "No news" message
else:
    messages = format_messages(articles)
    send_to_telegram(messages)
