#!/usr/bin/python3
import sys
import urllib3
import certifi
import sqlite3
import smtplib
import feedparser
from email.mime.text import MIMEText


db_connection = sqlite3.connect('magazine_rss.sqlite')
db = db_connection.cursor()
db.execute('CREATE TABLE IF NOT EXISTS magazine (title TEXT, date TEXT)')


def article_is_not_db(article_title, article_date):
    """ Check if a given pair of article title and date
    is in the database.
    Args:
        article_title (str): The title of an article
        article_date  (str): The publication date of an article
    Return:
        True if the article is not in the database
        False if the article is already present in the database
    """
    db.execute("SELECT * from magazine WHERE title=? AND date=?", (article_title, article_date))
    if not db.fetchall():
        return True
    else:
        return False


def add_article_to_db(article_title, article_date):
    """ Add a new article title and date to the database
    Args:
        article_title (str): The title of an article
        article_date (str): The publication date of an article
    """
    db.execute("INSERT INTO magazine VALUES (?, ?)", (article_title, article_date))
    db_connection.commit()


def send_notification(article_title, article_url):
    """ Send a notification email
    Args:
        article_title (str): The title of an article
        article_url (str): The url to access the article
    """

    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.login('your_email@gmail.com', '123your_password')
    msg = MIMEText(f'\nHi there is a new Fedora Magazine article : {article_title}. \nYou can read it here {article_url}')
    msg['Subject'] = 'New Fedora Magazine Article Available'
    msg['From'] = 'your_email@gmail.com'
    msg['To'] = 'destination_email@gmail.com'
    smtp_server.send_message(msg)
    smtp_server.quit()


def send_telegram_notification(article_title, article_url):
    """ Send a notification message to a Telegram chat
    using your own bot
    Docs: https://core.telegram.org/bots
    Args:
        article_title (str): The title of an article
        article_url (str): The url to access the article
    """
    bot_id = ''
    chat_id = ''

    try:
        https = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        r = https.request('GET', 'https://api.telegram.org/bot'
                        + bot_id + '/sendMessage?chat_id='
                        + chat_id + '&text=' + article_title + article_url)
    except urllib3.exceptions.SSLError as err:
        print('[ERROR] Telegram SSL error', err)
        sys.exit()


def read_article_feed():
    """ Get articles from RSS feed """
    feed = feedparser.parse('https://fedoramagazine.org/feed/')
    for article in feed['entries']:
        if article_is_not_db(article['title'], article['published']):
            ### Email notification
            send_notification(article['title'], article['link'])
            ### Telegram notification
            #send_telegram_notification(article['title'], article['link'])
            add_article_to_db(article['title'], article['published'])


if __name__ == '__main__':
    read_article_feed()
    db_connection.close()
