import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
import smtplib
from email.message import EmailMessage

load_dotenv("./.env")

MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = os.getenv("STOCK_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

today = datetime.now().date()
yesterday = today - timedelta(days=1)
day_before_yesterday = today - timedelta(days=2)

news_parameters = {
    "apiKey": NEWS_API_KEY,
    "q": STOCK,
    "from": f"{day_before_yesterday}",
    "to": f"{yesterday}",
    "language": "en",
    "searchIn": "description",
    "pageSize": 5,
}

news_response = requests.get(url=NEWS_ENDPOINT, params=news_parameters)
news_response.raise_for_status()
news_articles = news_response.json()["articles"][0:3]

stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "outputsize": "compact",
    "apikey": STOCK_API_KEY,
}

stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_parameters)
stock_response.raise_for_status()
stock_data = stock_response.json()["Time Series (Daily)"]

day_before_yesterday_closing_price = float(stock_data[f"{day_before_yesterday}"]['4. close'])
yesterday_closing_price = float(stock_data[f"{yesterday}"]['4. close'])

percentage_difference = (yesterday_closing_price
                         - day_before_yesterday_closing_price) * 100 / day_before_yesterday_closing_price

if percentage_difference > 5 or percentage_difference < -5:
    up_down = "🔺"
    if percentage_difference < 0:
        up_down = "🔻"
    for news in news_articles:
        subject = f"{STOCK}:{up_down}{percentage_difference:.2f}% ,{news['title']}"
        body = f"{news['description']}\n Read here: {news['url']}"
        message = EmailMessage()
        message.add_header("From", MY_EMAIL)
        message.add_header("To", MY_EMAIL)
        message.add_header("Subject", subject)
        message.set_payload(body, "utf-8")

        with smtplib.SMTP(host="smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=MY_PASSWORD)
            connection.send_message(from_addr=MY_EMAIL, to_addrs=MY_EMAIL, msg=message)
