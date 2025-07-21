import os
import requests

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_tech_news():
    url = "https://hn.algolia.com/api/v1/search?tags=story&query=technology"
    res = requests.get(url)

    if res.status_code != 200:
        return "Failed to fetch tech news."

    articles = res.json().get('hits', [])[:5]
    if not articles:
        return "No tech news found today."

    # Create a summary with title and description/snippet (if available)
    summaries = []
    for i, article in enumerate(articles, start=1):
        title = article.get("title", "No title")
        snippet = article.get("story_text") or article.get("comment_text") or "No summary available."
        if snippet and len(snippet) > 300:
            snippet = snippet[:300] + "..."

        summaries.append(f"*{i}. {title}*\n_{snippet}_")

    return "*📰 Today's Top Tech News*\n\n" + "\n\n".join(summaries)

def send_to_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    response = requests.post(telegram_url, data=data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    msg = get_tech_news()
    send_to_telegram(msg)
