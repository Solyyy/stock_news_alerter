import requests
import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load .env file
load_dotenv("C:\Python\env data.env")

# CONSTANTS
STOCK_NAME = "GME"
COMPANY_NAME = "GameStop Corporation"

# Alpha Vantage API Constants
AV_API_KEY = os.getenv("AV_API_KEY")
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
stock_api_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": AV_API_KEY
}

# News API Constants
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
news_api_parameters = {
    "q": COMPANY_NAME,
    "apiKey": NEWS_API_KEY
}

# Twilio API Constants
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NO = "+13187128318"
RECEIVER = os.getenv("MY_PHONE_NR")

# Request to AV API to receive closing stock price of yesterday and the day before yesterday
response = requests.get(url=STOCK_ENDPOINT, params=stock_api_parameters)
response.raise_for_status()
av_data = response.json()
stock_close_prices = av_data["Time Series (Daily)"]

# Getting the date from json response for yesterday and the day before yesterday
yesterday_date = list(av_data["Time Series (Daily)"].keys())[1]
day_before_yesterday_date = list(av_data["Time Series (Daily)"].keys())[2]

# Getting the stock price at markt close for yesterday and the day before.
yesterday_price = round(float(av_data["Time Series (Daily)"][yesterday_date]["4. close"]))
day_before_yesterday_price = round(float(av_data["Time Series (Daily)"][day_before_yesterday_date]["4. close"]))

# Calculating the percentage difference for the stock price between yesterday and the day before yesterday
stock_price_difference = yesterday_price - day_before_yesterday_price
stock_percentage_difference = round(stock_price_difference / day_before_yesterday_price * 100)

if stock_percentage_difference >= 5 or stock_percentage_difference <= -5:
    # Request to News API to receive top 3 news articles.
    news_api_request = requests.get(NEWS_ENDPOINT, params=news_api_parameters)
    news_api_request.raise_for_status()
    news_api_data = news_api_request.json()

    # Getting the first 3 articles from the news_api
    articles = [news for news in news_api_data["articles"][:3]]
    news_body = ""
    for msg in articles:
        news_body += "".join(f"Headline: {msg['title']}\n"
                             f"Brief: {msg['description']}\n\n")

    if stock_price_difference > 0:
        # Request Twilio API to send a txt message to my phone nr.
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages \
            .create(
                body=f"{STOCK_NAME} {stock_percentage_difference}%🔺\n"
                     f"{news_body}",
                from_=TWILIO_PHONE_NO,
                to=RECEIVER)
    elif stock_price_difference < 0:
        # Request Twilio API to send a txt message to my phone nr.
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages \
            .create(
                body=f"{STOCK_NAME} {abs(stock_percentage_difference)}%🔻\n"
                     f"{news_body}",
                from_=TWILIO_PHONE_NO,
                to=RECEIVER)
    else:
        print("There was no change in stock price today.")

