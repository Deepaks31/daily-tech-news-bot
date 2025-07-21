import requests
import os

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
NEWS_API_KEY = os.environ['NEWS_API_KEY']

# Get top tech news
def fetch_news():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": "technology",
        "language": "en",
        "pageSize": 10,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("articles", [])

# Summarize using OpenAI (mocked with description fallback)
def summarize(article):
    if article["description"]:
        return article["description"]
    elif article["content"]:
        return article["content"].split("…")[0]
    else:
        return "_No summary available._"

# Format and send message
def send_to_telegram(articles):
    message = "📰 *Today's Top Tech News*\n\n"
    for idx, article in enumerate(articles, start=1):
        title = article["title"]
        summary = summarize(article)
        message += f"*{idx}. {title}*\n_{summary}_\n\n"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, json=payload)
    print("Status:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    articles = fetch_news()
    if articles:
        send_to_telegram(articles)
    else:
        print("No articles found.")
