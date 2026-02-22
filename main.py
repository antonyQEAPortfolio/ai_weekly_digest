import feedparser
import datetime
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

RSS_FEEDS = {
    "OpenAI": "https://openai.com/blog/rss",
    "Anthropic": "https://www.anthropic.com/news/rss",
    "Google AI": "https://blog.google/technology/ai/rss/",
    "HuggingFace": "https://huggingface.co/blog/feed.xml"
}

def fetch_articles():
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    collected_articles = {}

    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        source_articles = []

        for entry in feed.entries:
            if hasattr(entry, "published_parsed"):
                published_date = datetime.datetime(*entry.published_parsed[:6])
                if published_date > one_week_ago:
                    source_articles.append({
                        "title": entry.title,
                        "link": entry.link
                    })

        if source_articles:
            collected_articles[source] = source_articles

    return collected_articles


def generate_email_content(articles):
    html = """
    <html>
    <body style="font-family: Arial;">
        <h2>🧠 Weekly AI Digest (Free Version)</h2>
        <hr>
    """

    if not articles:
        html += "<p>No major AI updates this week.</p>"
    else:
        for source, items in articles.items():
            html += f"<h3>{source}</h3><ul>"
            for item in items:
                html += f'<li><a href="{item["link"]}">{item["title"]}</a></li>'
            html += "</ul>"

    html += """
        <hr>
        <p style="font-size:12px;color:gray;">
        Automated AI Radar System (No API Used)
        </p>
    </body>
    </html>
    """

    return html


def send_email(content):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🧠 Weekly AI Digest"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL

    msg.attach(MIMEText(content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())


def main():
    print("Fetching articles...")
    articles = fetch_articles()

    print("Generating email...")
    email_content = generate_email_content(articles)

    print("Sending email...")
    send_email(email_content)

    print("Weekly digest sent successfully!")


if __name__ == "__main__":
    main()