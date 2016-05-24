from twython import Twython, TwythonAuthError, TwythonRateLimitError
from keys import APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from datetime import datetime
import os
import csv
import time
import json

INPUT_FILE_NAME = './data/raw/users/user_list.csv'
FILTER_DIR = './data/raw/tweets/'
OUTPUT_DIR = FILTER_DIR + 'user_data_5/'
ERROR_FILE_NAME = './data/raw/users/protected_users.csv'
MAX_TWEETS_ALLOWED = 32000
TWEETS_PER_REQUEST = 200
UPDATE_INTERVAL = 1
SLEEP_INTERVAL = 310

input_file = open(INPUT_FILE_NAME, 'rt')
user_list = csv.reader(input_file)
filter_set = set()
for root, directories, filenames in os.walk(FILTER_DIR):
    [filter_set.add(int(file.split('_')[0])) for file in filenames]
error_file = open(ERROR_FILE_NAME, 'a')
twitter = Twython(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
for user_tuple in user_list:
    user_id = int(user_tuple[0])
    got_count = 0
    saved_count = 0
    protected = 0
    if user_id not in filter_set:
        output_file_name = OUTPUT_DIR + user_tuple[0]
        tweet_store = open(output_file_name + '.txt', 'w')
        max_id = float('inf')
        first_iter = True
        while True:
            try:
                if first_iter:
                    timeline = twitter.get_user_timeline(
                        user_id=user_id, trim_user=True, include_rts=True, count=MAX_TWEETS_ALLOWED)
                    first_iter = False
                else:
                    timeline = twitter.get_user_timeline(
                        user_id=user_id, trim_user=True, include_rts=True, count=MAX_TWEETS_ALLOWED, max_id=max_id - 1)
                got_count += len(timeline)
                print(len(timeline), 'tweets retrieved. Current max id=', max_id)
                if not timeline:
                    break
                for tweet in timeline:
                    tweet_store.write(json.dumps(tweet))
                    tweet_store.write('\n')
                    saved_count += 1
                    max_id = min(max_id, tweet['id'])
            except TwythonRateLimitError as e:
                print(e)
                time.sleep(SLEEP_INTERVAL)
            except TwythonAuthError as e:
                print('Unauthorised to access timeline for user=', user_id)
                error_file.write(str(user_id) + '\n')
                protected = 1
                break
        tweet_store.close()
        if protected:
            os.rename(output_file_name + '.txt', './junk/' + str(user_id) + '.txt')
        else:
            print('Retrieved tweets for=', user_id, '\nTotal tweets retrieved=',
                  got_count, '\nTotal tweets saved=', saved_count)
            os.rename(output_file_name + '.txt', output_file_name +
                      '_' + str(saved_count) + '.txt')
input_file.close()
error_file.close()
