#Import necessary methods from Tweepy Library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import heapq
import time

#Variables that contains the user credentials to access Twitter API
access_token = "jWwEIoB8RqRXn6FSBPyQkMAyz"
access_token_secret = "6Hl4AC7KRktyjZSFmGClI8rMztBEbZSiDdJfJgQYsDPOAWSrXF"
consumer_key = "478337335-34ls4LJEllGMlQnd6UsS1UFOwxG2H5smbOKSuyOF"
consumer_secret = "BI1b8x4n1acXALRjGlmtAv1cXEvuVuF7r46jmHzG4eMH2"

top_n_results = 10

class retweeted():

    def __init__(self, text, n_minute_window, time):
        self.text = text
        self.n = n_minute_window
        self.retweet_times = []
        self.retweet_times.append(time)

    def add_retweet_time(self, t):
        self.retweet_times.append(t)

    def refresh_window(self):
        current_time = time.mktime(time.gmtime())
        time_window = current_time - self.n * 60
        for t in self.retweet_times:
            if t < time_window:
                self.retweet_times.remove(t)
            else:
                break

    def get_text(self):
        return self.text

    def get_retweet_num(self):
        return len(self.retweet_times)


class retweetListener(StreamListener):

    def __init__(self, n_minute_window):
        self.retweeteds = {}
        self.n = n_minute_window

    def on_data(self, data):
        tweet = json.loads(data)
        ret = tweet['retweeted_status']

        if ret:
            retweet_time = time.mktime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            retweeted_id = ret['id']

            if not retweeted_id in self.retweeteds:
                r = retweeted(ret['text'], self.n, retweet_time)
                self.retweeteds[retweeted_id] = r
            else:
                self.retweeteds[retweeted_id].add_retweet_time(retweet_time)

        self.refresh()
        self.print_top()
        return True

    def on_error(self, status):
        print status

    def refresh(self):
        for id in self.retweeteds.keys():
            self.retweeteds[id].refresh_window()
            if self.retweeteds[id].get_retweet_num() == 0:
                del self.retweeteds[id]

    def print_top(self):
        top = heapq.nlargest(top_n_results, self.retweeteds, key = lambda k: self.retweeteds[k].get_retweet_num())
        for i in range(len(top)):
            retweeted = top[i]
            print i + ". " + retweeted.get_text() + ": " + retweeted.get_retweet_num()
        print "\n"


if __name__ == '__main__':

    n = raw_input('Enter n, the time window in minutes: ')

    #Handles Twitter authentication and connection to Twitter Streaming API
    l = retweetListener(n)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    stream.sample()