import tweepy
import os
from dotenv import load_dotenv
import datetime
import time

bot_id = 1527806388457676802

today = datetime.datetime.now()
delta_time = datetime.timedelta(days=7)
week_ago = today - delta_time


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
                           access_token_secret=ACCESS_TOKEN_SECRET,
                           wait_on_rate_limit=True)
    return client


def add_to_best_tweet(tweet_id, tweet_likes, best_tweet):
    best_tweet.append(tweet_id)
    best_tweet.append(tweet_likes)

    return best_tweet


def main():
    client = config()
    res_user_id = client.get_users_following(bot_id, user_fields=["protected"])  # get user id and protected bool

    best_tweets = [0, 0]  # array to collect the most liked tweets
    page_token = None  # variable to save next_token
    has_next_token = True  # variable to check if next_token exists

    # run through all user that the bot is following
    for user_id in res_user_id.data:
        #print(f"user_id under the for-loop {user_id}")

        # filter through the users that have the tweets 'protected'
        if not user_id.protected:

            # go through all tweets till there is no more next_token's
            while has_next_token:
                # get all tweets from the last 7 days
                res_tweets = client.get_users_tweets(user_id.id, end_time=today, exclude="retweets", max_results=100, pagination_token=page_token, start_time=week_ago, tweet_fields=["public_metrics"])
                # try as long as there is data
                try:
                    for tweet in res_tweets.data:
                        # try as long as there is a next_token key
                        try:
                            next_token = res_tweets.meta["next_token"]
                            # if the tokens are not the same save the new one in the variable page_token
                            if page_token != next_token:
                                page_token = next_token
                                #print(page_token)
                        except KeyError:
                            has_next_token = False  # get out of the while loop for the next user
                            page_token = None
                            print("Key Error, no next_token")
                        # save the id and likes in the variables
                        tweet_id = tweet.id
                        tweet_likes = tweet.public_metrics["like_count"]

                        # if there are more tweets with the same like-count add them to the array
                        if tweet_likes == best_tweets[1]:
                            best_tweets = add_to_best_tweet(tweet_id, tweet_likes, best_tweets)
                        # else if the likes are higher than the one in the list clear the array and add it
                        elif tweet_likes > best_tweets[1]:
                            best_tweets.clear()
                            best_tweets = add_to_best_tweet(tweet_id, tweet_likes, best_tweets)
                        #print(f"{tweet.text} ------ {best_tweets[1]}")
                except TypeError:
                    print(f"Get Users Tweets Response is {res_tweets.data}")
                    break
            has_next_token = True  # reset boolean to let the next user enter the while-loop

    # if there are multiple tweets in the array go to every second index to grab the tweet_id
    for index, tw_id in enumerate(best_tweets[::2]):
        #print(tw_id)
        best_tweet = client.get_tweet(best_tweets[index], tweet_fields=["text"])
        print(f"MOST LIKED TWEET!! ---> {best_tweet.data.text}")
        try:
            client.create_tweet(text=f"❤Week {today.strftime('%V')}❤\n Most liked tweet is: \n https://twitter.com/SenshiSuni/status/{tw_id}")
        except tweepy.errors.Forbidden as e:
            print(f"Tweet already exists. Status: {e}")
        # TODO save the tweet_id and likes in a JSON in this structure: 'Year' -> 'Week' -> 'tweet_id', 'likes'
        time.sleep(5)
    #print(best_tweet.data["username"])


if __name__ == '__main__':
    main()
