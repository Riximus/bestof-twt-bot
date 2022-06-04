import tweepy
import os
from dotenv import load_dotenv
import datetime
import time

bot_id = 1527806388457676802

today = datetime.datetime.now()
delta_time = datetime.timedelta(days=7)
week_ago = today - delta_time
seperator = '\n'


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


# Placing the ranking
def dict_forming(best_tweets: dict, t_id, t_likes) -> dict:
    for _, first_val in best_tweets[1].items():  # checks first place last
        for _, second_val in best_tweets[2].items():
            for _, third_val in best_tweets[3].items():  # checks third place first

                if third_val > t_likes:  # if likes are not top 3
                    return best_tweets

                # THIRD PLACE
                elif third_val < t_likes:
                    # SECOND PLACE
                    if second_val < t_likes:
                        # FIRST PLACE
                        if first_val <= t_likes:
                            if first_val < t_likes:
                                best_tweets[1].clear()
                            best_tweets[1][t_id] = t_likes
                        elif first_val > t_likes:
                            best_tweets[2].clear()
                            best_tweets[2][t_id] = t_likes
                        return best_tweets

                    elif second_val == t_likes:
                        best_tweets[2][t_id] = t_likes
                    else:
                        best_tweets[3].clear()
                        best_tweets[3][t_id] = t_likes
                    return best_tweets

                elif third_val == t_likes:
                    best_tweets[3][t_id] = t_likes
                return best_tweets

    return best_tweets


def get_best_tweet(best_tweets, client, place, previous_tweet):
    tweet_link = f"https://twitter.com/user/status/"
    place_text = None
    text_more_ids = ""

    match place:
        case 1:
            place_text = "🥇 Most"
        case 2:
            place_text = "🥈 Second most"
        case 3:
            place_text = "🥉 Third most"
    text_one_id = f"❤Week {today.strftime('%V')}❤\n {place_text} liked tweet(s) is:"

    for index, twt_id in enumerate(best_tweets[place]):
        # best_tweet = client.get_tweet(best_tweets[place][twt_id], tweet_fields=['text'])
        # print(f"MOST LIKED TWEET!! ---> ")#{best_tweet.data.text}")
        try:
            is_only_one_tweet = len(best_tweets[place]) == 1
            if is_only_one_tweet:
                return client.create_tweet(text=f"{text_one_id}\n{tweet_link}{twt_id}",
                                           in_reply_to_tweet_id=previous_tweet)

            text_more_ids += f"\n{tweet_link}{twt_id}\n"  # store multiple links in one string to print them all out

            is_last_tweet_url = index == len(best_tweets[place])
            if is_last_tweet_url:
                text_one_id += text_more_ids  # add the stored links to the presenting text
                return client.create_tweet(text=text_one_id, in_reply_to_tweet_id=previous_tweet)

        except tweepy.errors.Forbidden as e:
            print(f"Tweet already exists. Status: {e}")
            # TODO save the tweet_id and likes in a JSON in this structure: 'Year' -> 'Week' -> 'tweet_id', 'likes'
        time.sleep(5)
    return None


# # # --- MAIN --- # # #
def main():
    client = config()
    res_user_id = client.get_users_following(bot_id, user_fields=["protected"])  # get user id and protected bool

    # TODO use my_dict.update({key: value}) and/or my_dict.update({key: {key: value}}) instead of my_dict['key'] = value
    best_tweets = {1: {1: -1},  # ID: Likes
                   2: {1: -1},
                   3: {1: -1}}  # array to collect the most liked tweets
    tweet_stats = {'following': 0,
                   'tweet_count': 0,
                   'like_count': 0,
                   'most_tweeter': {0: 0}}  # ID: Likes # implement later

    page_token = None  # variable to save next_token
    has_next_token = True  # variable to check if next_token exists
    user_tweet_count = 0

    # run through all user that the bot is following
    for user_id in res_user_id.data:

        # filter through the users that have the tweets 'protected'
        if not user_id.protected:
            tweet_stats['following'] += 1  # count the users that are not protected

            # go through all tweets till there is no more next_token's
            while has_next_token:
                # get all tweets from the last 7 days
                res_tweets = client.get_users_tweets(user_id.id, end_time=today, exclude="retweets", max_results=100,
                                                     pagination_token=page_token, start_time=week_ago,
                                                     tweet_fields=["public_metrics"])
                # try as long as there is data
                try:
                    for tweet in res_tweets.data:
                        tweet_stats['tweet_count'] += 1  # count the tweets
                        user_tweet_count += 1
                        # try as long as there is a next_token key
                        try:
                            next_token = res_tweets.meta["next_token"]
                            # if the tokens are not the same save the new one in the variable page_token
                            if page_token != next_token:
                                page_token = next_token
                                # print(page_token)
                        except KeyError:
                            has_next_token = False  # get out of the while loop for the next user
                            page_token = None
                            # print("Key Error, no next_token")
                        # save the id and likes in the variables
                        tweet_id = tweet.id
                        tweet_likes = tweet.public_metrics["like_count"]
                        tweet_stats['like_count'] += tweet_likes  # sum all likes together

                        best_tweets = dict_forming(best_tweets, tweet_id, tweet_likes)

                except TypeError:
                    print(f"Get Users Tweets Response is {res_tweets.data}")
                    break
            has_next_token = True  # reset boolean to let the next user enter the while-loop

        # collect for the stats the user that tweeted the most
        for _, tweets in tweet_stats['most_tweeter'].items():
            if tweets <= user_tweet_count:  # checks if the user has more or equal tweets than the current in the dictionary
                if tweets < user_tweet_count:
                    tweet_stats['most_tweeter'].clear()
                tweet_stats['most_tweeter'][user_id.id] = user_tweet_count
            user_tweet_count = 0
            break

    # tweet the tweets in the order of most liked and add the next place as a response
    previous_tweet = None
    dict_len = len(best_tweets)

    # go through all tweets
    for i in range(1, dict_len + 1):
        created_tweet = get_best_tweet(best_tweets, client, i, previous_tweet)  # The account tweets the best tweets
        print(created_tweet)  # Debugging
        created_tweet_res = created_tweet.data
        previous_tweet = created_tweet_res["id"]  # get the id from the created tweet to use it to respond to
        print(f"Previous ID: {previous_tweet}")

    most_tweeter = tweet_stats['most_tweeter']  # store the most tweeters
    username_tweet = {}

    # store the amount of tweets(value) to the username(key)
    for t_id, t_count in most_tweeter.items():
        user_data = client.get_user(id=t_id).data
        username_tweet[user_data['username']] = t_count  # new dictionary to loop for the tweet text in the f-string

    # user_data = [client.get_user(id=key).data for key in most_tweeter]
    # STATS OUTPUT
    client.create_tweet(text=f"📊 Some Stats 📊\n"
                             f"---------------------\n"
                             f"👥Users: {tweet_stats['following']}\n"
                             f"🐦Tweets: {tweet_stats['tweet_count']}\n"
                             f"💕Likes: {tweet_stats['like_count']}\n"
                             f"➗Ø-Like: {int(tweet_stats['like_count'] / tweet_stats['tweet_count'])}\n"
                             f"✍️Tweeted the most\n"
                             f"{seperator.join(f'@{key} -> {value}' for key, value in username_tweet.items())}",
                        in_reply_to_tweet_id=previous_tweet)


if __name__ == '__main__':
    main()
