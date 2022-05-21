import tweepy
import requests
import os
from dotenv import load_dotenv


def config():
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    API_KEY_SECRET = os.getenv("API_KEY_SECRET")
    BEARER_TOKEN = os.getenv("BEARER_TOKEN")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
    CONSUMER_KEY = os.getenv("CONSUMER_KEY")
    CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")

    client = tweepy.Client(bearer_token=BEARER_TOKEN,
                           consumer_key=API_KEY,
                           consumer_secret=API_KEY_SECRET,
                           access_token=ACCESS_TOKEN,
                           access_token_secret=ACCESS_TOKEN_SECRET)
    #auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
    #auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    #api = tweepy.API(auth, wait_on_rate_limit=True)

    return client


def main():
    client = config()
    response = client.create_tweet(text='Hello World und so')
    print(response)


if __name__ == '__main__':
    main()
