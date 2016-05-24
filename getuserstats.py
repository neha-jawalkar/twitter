import csv
import json
import glob
from datetime import datetime

INPUT_FILE_NAME = './data/raw/users/user_data_5.csv'
OUTPUT_FILE_NAME = './data/processed/' + INPUT_FILE_NAME.split('/')[-1]
TWEET_STORE_ROOT_DIR = './data/raw/tweets/'
TWEET_STORE_DIR = TWEET_STORE_ROOT_DIR + \
    INPUT_FILE_NAME.split('/')[-1].split('.')[0] + '/'

input_file = open(INPUT_FILE_NAME, 'rt')
users = csv.reader(input_file)
output_file = open(OUTPUT_FILE_NAME, 'w')
output_file.write(','.join(['ID', 'CREATED_AT', 'STATUSES_COUNT', 'FRIENDS_COUNT', 'LISTED_COUNT', 'USER_FAVORITES', 'HAS_BEEN_VERIFIED',
                            'FOLLOWERS_COUNT', 'DESCRIPTION_LEN', 'HAS_URL', 'HAS_LOCATION', 'REPLIES', 'MENTIONS',
                            'RETWEETS_OF_USER_TWEETS', 'RETWEETS_BY_USER', 'FAVORITE_COUNT_FOR_USER', 'HASHTAGS', 'BROADCAST_COMMS',
                            'QUOTES', 'URLS','TWEETS_EXAMINED']) + '\n')
for user in users:
    user_id = user[0]
    tweet_store = None
    tweets_in_store = 0
    for file in glob.glob(TWEET_STORE_DIR + user_id + '_*.txt'):
        print('User=', user_id, '\nFound file=', file)
        tweet_store = open(file, 'r')
        tweets_in_store = int(file.split('/')[-1].split('_')[1].split('.')[0])
    if not tweet_store:
        print('No tweet store found for user=', user_id)
        continue
    replies = mentions = retweets_of_user_tweets = retweets_by_user = favorite_count_for_user = hashtags = broadcast_comms = quotes = urls = tweets_examined = 0
    for line in tweet_store:
        tweet = json.loads(line)
        if 'retweeted_status' in tweet:
            retweets_by_user += 1
        else:
            if 'retweet_count' in tweet and tweet['retweet_count']:
                retweets_of_user_tweets += tweet['retweet_count']
            if 'favorite_count' in tweet and tweet['favorite_count']:
                favorite_count_for_user += tweet['favorite_count']
            if 'in_reply_to_user_id' in tweet and tweet['in_reply_to_user_id']:
                replies += 1
            if 'quoted_status_id' in tweet:
                quotes += 1
            if 'entities' in tweet and tweet['entities']:
                if 'user_mentions' in tweet['entities'] and tweet['entities']['user_mentions']:
                    mentions += len(tweet['entities']['user_mentions'])
                else:
                    broadcast_comms += 1
                if 'hashtags' in tweet['entities'] and tweet['entities']['hashtags']:
                    hashtags += len(tweet['entities']['hashtags'])
                if 'urls' in tweet['entities'] and tweet['entities']['urls']:
                    urls += len(tweet['entities']['urls'])
        tweets_examined += 1

    print('Tweets in store=', tweets_in_store)
    print('Tweets examined=', tweets_examined)
    print('Communication index=', broadcast_comms + mentions + retweets_by_user)
    stats = [replies, mentions, retweets_of_user_tweets, retweets_by_user,
             favorite_count_for_user, hashtags, broadcast_comms, quotes, urls, tweets_examined]
    stats_str = [str(stat) for stat in stats]
    user_tuple = user + stats_str
    output_file.write(','.join(user_tuple) + '\n')
output_file.close()
