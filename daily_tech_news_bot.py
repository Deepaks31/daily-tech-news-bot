import requests
import os

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
NEWS_API_KEY = os.environ['NEWS_API_KEY']

def fetch_tech_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&category=technology&language=en"
    res = requests.get(url).json()
    return res['results'][:10]  # Top 10

def summarize_text(text):
    url = "https://api.aiforthings.com/summarize"  # Example summarizer API
    response = requests.post(url, json={"text": text})
    return response.json().get("summary", "No summary available.")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def main():
    news_list = fetch_tech_news()
    message = "📰 <b>Today's Top Tech News</b>\n\n"

    for idx, news in enumerate(news_list, 1):
        title = news.get('title')
        content = news.get('description') or news.get('content', '')
        summary = summarize_text(content) if content else "No summary available."
        message += f"<b>{idx}. {title}</b>\n{summary}\n\n"

    send_telegram_message(message)

if __name__ == "__main__":
    main()
