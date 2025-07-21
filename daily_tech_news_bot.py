import os
import requests
from telegram import Bot
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Load secrets from environment
TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('CHAT_ID')
NEWSDATA_API_KEY = os.environ.get('NEWS_API_KEY')

def summarize_text(text, sentence_count=2):
    if not text or len(text.split()) < 20:
        return text.strip()
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return ' '.join(str(sentence) for sentence in summary)

def fetch_top_tech_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&category=technology&language=en"
    try:
        response = requests.get(url)
        data = response.json()
        print("🔍 Full API Response:")
        print(data)  # ← Add this line to inspect the real response
    except Exception as e:
        print("❌ Error fetching/parsing API:", e)
        return []

    if data.get("status") != "success":
        print("❌ API Error:", data.get("message", "Unknown error"))
        return []

    articles = data.get("results")
    if not isinstance(articles, list):
        print("❌ No valid 'results' found.")
        return []

    return articles[:10]


def format_news(news_list):
    formatted = "📰 *Top Tech News Today*\n\n"
    for idx, article in enumerate(news_list, 1):
        title = article.get("title", "No title")
        description = article.get("description", "")
        content = article.get("content", "")
        summary_source = description or content or title
        brief = summarize_text(summary_source)
        formatted += f"🔹 *{title}*\n_{brief}_\n\n"
    return formatted

def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    # Split if message exceeds Telegram limit
    for i in range(0, len(message), 4000):
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message[i:i+4000], parse_mode="Markdown")

def main():
    news_list = fetch_top_tech_news()
    if not news_list:
        print("⚠️ No articles found or failed to fetch news.")
        return

    message = format_news(news_list)

    if len(message) > 0:
        send_telegram_message(message)
        print("✅ News sent successfully.")
    else:
        print("⚠️ No message content to send.")

if __name__ == "__main__":
    main()
