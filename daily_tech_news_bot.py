import os
import requests
from telegram import Bot
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Load from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('CHAT_ID')
NEWSDATA_API_KEY = os.environ.get('NEWS_API_KEY')

def summarize_text(text, sentence_count=2):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return ' '.join(str(sentence) for sentence in summary)

def fetch_top_tech_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&category=technology&language=en"
    response = requests.get(url)
    data = response.json()
    
    if "results" not in data or not data["results"]:
        return []

    return data["results"][:10]  # Get top 10 tech news articles

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
    # Telegram allows max 4096 chars per message
    for i in range(0, len(message), 4000):
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message[i:i+4000], parse_mode="Markdown")

def main():
    news_list = fetch_top_tech_news()
    if not news_list:
        print("No articles found.")
        return
    message = format_news(news_list)
    send_telegram_message(message)
    print("News sent successfully.")

if __name__ == "__main__":
    main()
