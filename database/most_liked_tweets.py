import pprint
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import datetime
import os
from dotenv import load_dotenv

# Name for log file
date = datetime.date.today()
today = datetime.datetime.now()
week = today.strftime("%V")
logfile = f'logs/{date}_W{week}.txt'

# MostLikedTweets Database Collection Document Templates
posted_tweets_template = {
    "year": str(today.year),
    "week": week,
    "gold": {
        "user_ids": [],
        "tweet_ids": [],
        "likes": []
    },
    "silver": {
        "user_ids": [],
        "tweet_ids": [],
        "likes": []
    },
    "bronze": {
        "user_ids": [],
        "tweet_ids": [],
        "likes": []
    },
    "stats": {
        "users_total": "",
        "tweets_total": "",
        "likes_total": "",
        "likes_avg": "",
        "tweeted_most": {
            "user_id": [],
            "tweets_count": []
        }
    }
}


# Database Connection
def _db_config():
    load_dotenv()
    MONGOUSER = os.getenv("MONGOUSER")
    MONGOPASSWORD = os.getenv("MONGOPASSWORD")
    MONGOHOST = os.getenv("MONGOHOST")
    MONGOPORT = os.getenv("MONGOPORT")
    CONNECTION_URL = f'mongodb://{MONGOUSER}:{MONGOPASSWORD}@{MONGOHOST}:{MONGOPORT}'

    client = MongoClient(CONNECTION_URL)
    with open(logfile, 'a') as f:
        try:
            client.admin.command('ismaster')
        except ConnectionFailure:
            f.write("DATABASE\n"
                    "-----------\n"
                    "Connection Failure\n")
            return None
        except OperationFailure as e:
            if "Authentication failed" in str(e):
                f.write("DATABASE\n"
                        "-----------\n"
                        "Invalid Credentials\n")
            else:
                f.write("DATABASE\n"
                        "-----------\n"
                        "Connection Failure\n")
            return None
        except Exception as e:
            f.write("DATABASE\n"
                    "-----------\n"
                    f"Error connecting to MongoDB: {e}")
            return None
        else:
            f.write("DATABASE\n"
                    "-----------\n"
                    "Connection Successful\n")
            return client


def add_posted_tweets(best_tweets: dict, tweet_stats: dict):
    db_name = os.getenv("DB_NAME_LIKES")
    collection_name = os.getenv("COL_NAME_TWEETS_LIKES")
    posted_tweets_dict = posted_tweets_template

    client = _db_config()
    if client is None:
        return

    db = client[db_name]
    col_posted_tweets = db[collection_name]

    # add ranked tweets into the dictionary for the database
    for rank in best_tweets:
        match rank:
            case 1:
                # stringify the user ids
                for user_id in best_tweets[rank]["user_ids"]:
                    posted_tweets_dict["gold"]["user_ids"].append(str(user_id))
                # key -> tweet id, value -> tweet likes
                for key, value in best_tweets[rank]["tweets"].items():
                    key = str(key)
                    value = str(value)
                    posted_tweets_dict["gold"]["tweet_ids"].append(key)
                    posted_tweets_dict["gold"]["likes"].append(value)
            case 2:
                # stringify the user ids
                for user_id in best_tweets[rank]["user_ids"]:
                    posted_tweets_dict["silver"]["user_ids"].append(str(user_id))
                # key -> tweet id, value -> tweet likes
                for key, value in best_tweets[rank]["tweets"].items():
                    key = str(key)
                    value = str(value)
                    posted_tweets_dict["silver"]["tweet_ids"].append(key)
                    posted_tweets_dict["silver"]["likes"].append(value)
            case 3:
                # stringify the user ids
                for user_id in best_tweets[rank]["user_ids"]:
                    posted_tweets_dict["bronze"]["user_ids"].append(str(user_id))
                # key -> tweet id, value -> tweet likes
                for key, value in best_tweets[rank]["tweets"].items():
                    key = str(key)
                    value = str(value)
                    posted_tweets_dict["bronze"]["tweet_ids"].append(key)
                    posted_tweets_dict["bronze"]["likes"].append(value)

    # add tweet stats into the dictionary for the database
    posted_tweets_dict["stats"]["users_total"] = str(tweet_stats["following"])
    posted_tweets_dict["stats"]["tweets_total"] = str(tweet_stats["tweet_count"])
    posted_tweets_dict["stats"]["likes_total"] = str(tweet_stats["like_count"])
    posted_tweets_dict["stats"]["likes_avg"] = str(int(tweet_stats["like_count"] / tweet_stats["tweet_count"]))
    for key, value in tweet_stats["most_tweeter"].items():
        key = str(key)
        value = str(value)
        posted_tweets_dict["stats"]["tweeted_most"]["user_id"].append(key)
        posted_tweets_dict["stats"]["tweeted_most"]["tweets_count"].append(value)

    # LOGGING
    with open(logfile, 'a') as f:
        f.write("POSTED TWEETS DICTIONARY FOR DATABASE\n"
                "-------------------------------------------------\n")
        f.write(pprint.pformat(posted_tweets_dict))

    # create a new collection with adjusted dictionary
    try:
        col_id = col_posted_tweets.insert_one(posted_tweets_dict)
    except Exception as e:
        with open(logfile, 'a') as f:
            f.write(f"\nERROR INSERTING ONE\n"
                    f"-------------------------\n")
            f.write(f"{e}")
    else:
        with open(logfile, 'a') as f:
            f.write("\nINSERT SUCCESSFUL\n")
            f.write(pprint.pformat(col_id.inserted_id))

