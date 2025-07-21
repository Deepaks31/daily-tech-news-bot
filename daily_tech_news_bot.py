import os
import requests

# Environment variables for security
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

    news = "\n\n".join(
        [f"🔹 [{a['title']}]({a['url']})" for a in articles]
    )
    return f"*📰 Today's Tech News*\n\n{news}"

def send_to_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    response = requests.post(telegram_url, data=data)
    
    # Debug print in logs
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    msg = get_tech_news()
    send_to_telegram(msg)
