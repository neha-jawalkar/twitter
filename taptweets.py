from twython import TwythonStreamer
from keys import APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from datetime import datetime
import csv
import time


class TweetStreamer(TwythonStreamer):

    attr_list = ['id', 'created_at', 'statuses_count',
                 'friends_count', 'listed_count', 'favourites_count', 'verified', 'followers_count', 'description', 'url', 'location']
    SLEEP_INTERVAL = 5

    def __init__(self, streamer_settings):
        self.USER_FILTER_FILE = streamer_settings['USER_FILTER_FILE']
        user_filter_file = open(self.USER_FILTER_FILE, 'rt')
        user_list = csv.reader(user_filter_file)
        self.user_set = set()
        [self.user_set.add(user_id[0]) for user_id in user_list]
        user_filter_file.close()
        self.LIMITING_COUNT = streamer_settings['LIMITING_COUNT']
        self.UPDATE_INTERVAL = streamer_settings['UPDATE_INTERVAL']
        self.OUTPUT_FILE_NAME = streamer_settings['OUTPUT_FILE_NAME']
        self.output_file = open(self.OUTPUT_FILE_NAME, 'w')
        self.count = 0
        super(self.__class__, self).__init__(streamer_settings['APP_KEY'], streamer_settings[
            'APP_SECRET'], streamer_settings['ACCESS_TOKEN'], streamer_settings['ACCESS_TOKEN_SECRET'])

    def on_success(self, data):
        if 'user' in data:
            user = data['user']
            if user['id'] not in self.user_set:
                user_tuple = []
                [user_tuple.append(user[attr])
                 for attr in self.attr_list[:-3]]
                desc_len = 0
                if user[self.attr_list[-3]]:
                    desc_len = len(user[self.attr_list[-3]])
                user_tuple += [desc_len, bool(user[self.attr_list[-2]]),
                               bool(user[self.attr_list[-1]])]
                self.output_file.write(
                    ','.join([str(user_val) for user_val in user_tuple]) + '\n')
                self.user_set.add(user['id'])
                self.count = self.count + 1
                if self.count % self.UPDATE_INTERVAL == 0:
                    print(self.count, 'users saved.')
                if self.count >= self.LIMITING_COUNT:
                    self.disconnect()
                    self.output_file.close()
                    user_filter_file = open(self.USER_FILTER_FILE, 'w')
                    [user_filter_file.write(str(user_id) + '\n')
                     for user_id in self.user_set]
                    user_filter_file.close()

    def on_error(self, status_code, data):
        print('Error, status code ', status_code, '.')
        time.sleep(self.SLEEP_INTERVAL)


STREAMER_SETTINGS = {
    'APP_KEY': APP_KEY,
    'APP_SECRET': APP_SECRET,
    'ACCESS_TOKEN': ACCESS_TOKEN,
    'ACCESS_TOKEN_SECRET': ACCESS_TOKEN_SECRET,
    'LIMITING_COUNT': 100,
    'UPDATE_INTERVAL': 10,
    'USER_FILTER_FILE': './data/raw/users/user_list.csv',
    'OUTPUT_FILE_NAME': './data/raw/users/user_data_5.csv',
}

stream = TweetStreamer(STREAMER_SETTINGS)
stream.statuses.sample()
