"""
Daily AI News Emailer
----------------------
Fetches the latest AI news headlines + links from free RSS feeds
and emails them to you using your Gmail App Password.

No API keys needed for the news part (uses public RSS feeds).
"""

import os
import smtplib
import feedparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ---- RSS feeds to pull AI news from (free, no API key needed) ----
RSS_FEEDS = {
    "Google News - AI": "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-IN&gl=IN&ceid=IN:en",
    "TechCrunch - AI": "https://techcrunch.com/tag/artificial-intelligence/feed/",
}

MAX_ARTICLES_PER_FEED = 5


def fetch_news():
    """Fetch top headlines + links from each RSS feed."""
    all_news = {}
    for source_name, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
            title = entry.get("title", "Untitled")
            link = entry.get("link", "")
            articles.append((title, link))
        all_news[source_name] = articles
    return all_news


def build_email_html(news_by_source):
    """Format the news into a clean HTML email body."""
    today = datetime.now().strftime("%B %d, %Y")
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px; padding: 24px;">
            <h2 style="color: #111;">🧠 Daily AI News — {today}</h2>
    """
    for source, articles in news_by_source.items():
        html += f'<h3 style="color: #333; margin-top: 24px;">{source}</h3><ul style="padding-left: 20px;">'
        if not articles:
            html += "<li>No articles found today.</li>"
        for title, link in articles:
            html += f'<li style="margin-bottom: 8px;"><a href="{link}" style="color: #1a73e8; text-decoration: none;">{title}</a></li>'
        html += "</ul>"

    html += """
            <p style="color: #888; font-size: 12px; margin-top: 32px;">
                Sent automatically every morning via GitHub Actions.
            </p>
        </div>
    </body>
    </html>
    """
    return html


def send_email(html_body):
    """Send the email using Gmail SMTP + App Password (from GitHub Secrets)."""
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
    to_email = os.environ["TO_EMAIL"]

    today = datetime.now().strftime("%B %d, %Y")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🧠 Daily AI News — {today}"
    msg["From"] = gmail_address
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, to_email, msg.as_string())

    print("Email sent successfully!")


if __name__ == "__main__":
    news = fetch_news()
    html_body = build_email_html(news)
    send_email(html_body)
