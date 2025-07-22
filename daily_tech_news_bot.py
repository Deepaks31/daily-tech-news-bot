import requests
import os
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# Load secrets from environment
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Corrected API URL (using category, not q)
NEWS_API_URL = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&category=technology&language=en&page=1"

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Device set to use", device)

# Load summarizer
print("Loading summarizer...")
tokenizer = AutoTokenizer.from_pretrained("t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("t5-small").to(device)

def summarize_text(text):
    input_text = "summarize: " + text.strip().replace("\n", " ")
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True).to(device)

    input_len = inputs.shape[1]
    max_len = min(50, int(input_len * 0.5))
    outputs = model.generate(inputs, max_length=max_len, min_length=10, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary.strip()

def fetch_news():
    try:
        response = requests.get(NEWS_API_URL)
        response.raise_for_status()
        data = response.json()

        if "results" not in data or not data["results"]:
            print("No articles found.")
            return []

        news_summary = []
        for article in data["results"][:10]:
            title = article.get("title")
            description = article.get("description")

            if not title or not description:
                continue

            full_content = f"{title.strip()}. {description.strip()}"
            summary = summarize_text(full_content)

            news_summary.append(f"📰 *{title.strip()}*\n{summary}")

        return news_summary

    except Exception as e:
        print("Error fetching news:", e)
        return []

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    r = requests.post(url, json=payload)
    print("✅ Telegram Status:", r.status_code)

if __name__ == "__main__":
    news_summaries = fetch_news()
    if news_summaries:
        final_message = "📢 *Top Tech News Today*\n\n" + "\n\n".join(news_summaries)
    else:
        final_message = "⚠️ No tech news found today."

    send_telegram_message(final_message)
