import requests
import openai
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# --- CONFIGURATION ---
NEWS_API_KEY = 'f6759edd625843b9ad10bcd78ca450d8'
OPENAI_API_KEY = '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'
SENDGRID_API_KEY = 'SG._yrzv80sRjW0ySXGVu8bWg.hz0GqjNRcy9xNyhEFcF4S3G7_7ZEYPGjb15REQ0byRQ'

FROM_EMAIL = 'jchoover44@tntech.edu'
TO_EMAIL = 'jahileman42@tntech.edu'

# --- SET KEYS ---
openai.api_key = OPENAI_API_KEY

# --- FETCH TOP NEWS ---
def fetch_articles():
    url = f'https://newsapi.org/v2/top-headlines?country=us&pageSize=3&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data['articles'] if 'articles' in data else []

# --- SUMMARIZE USING OPENAI ---
def summarize_article(text):
    try:
        summary = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You summarize news articles."},
                {"role": "user", "content": f"Summarize this in 3-4 sentences:\n\n{text}"}
            ],
            max_tokens=200
        )
        return summary['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"(Error summarizing: {e})"

# --- BUILD EMAIL HTML ---
def create_email_content(articles):
    html = "<h2>📰 Today's News Summaries</h2><ul>"
    for i, article in enumerate(articles, start=1):
        title = article['title']
        url = article['url']
        content = article.get('content') or article.get('description') or ''
        summary = summarize_article(content)
        html += f"<li><strong>{title}</strong><br><a href='{url}'>Read full article</a><br><em>{summary}</em></li><br>"
    html += "</ul>"
    return html

# --- SEND EMAIL VIA SENDGRID ---
def send_email(subject, content_html):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject=subject,
        html_content=content_html
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Email sent! Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# --- MAIN ---
if __name__ == "__main__":
    articles = fetch_articles()
    if articles:
        email_html = create_email_content(articles)
        send_email("📰 Daily News Digest", email_html)
    else:
        print("No articles found.")
