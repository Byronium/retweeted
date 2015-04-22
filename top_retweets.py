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

top_x_results = 10

class retweeted():

    def __init__(self, time, text):
        self.retweet_times = []
        self.retweet_times.append(time)
        self.text = text

    def add_retweet_time(self, t):
        self.retweet_times.append(t)

    def get_text(self):
        return self.text

    def get_num_retweets(self):
        return len(self.retweet_times)
    
    def refresh_time_window(self, n):
        current_time = time.mktime(time.gmtime())
        time_window = current_time - n * 60
        for t in self.retweet_times:
            # remove all retweets beyond n-minutes in the past
            if t < time_window:
                self.retweet_times.remove(t)
            # tweet times are chronologically ascending,
            # so all future tweets should be within the window
            else:
                break


class retweetListener(StreamListener):

    def __init__(self, n_minute_window):
        # dictionary of ids to retweeted objects
        self.retweeteds = {}
        self.n = n_minute_window

    def on_data(self, data):
        tweet = json.loads(data)
        ret = tweet['retweeted_status']

        if ret:
            retweet_time = time.mktime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            retweeted_id = ret['id']

            if not (retweeted_id in self.retweeteds.keys()):
                retweet_text = ret['text']
                r = retweeted(retweet_text, retweet_time, self.n)
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
            self.retweeteds[id].refresh_time_window(self.n)
            if self.retweeteds[id].get_num_retweets() == 0:
                del self.retweeteds[id]

    def print_top(self):
        top = heapq.nlargest(top_x_results, self.retweeteds, key = lambda k: self.retweeteds[k].get_num_retweets())
        for i in range(len(top)):
            retweeted = top[i]
            print str(i) + ". " + retweeted.get_text() + ": " + str(retweeted.get_num_retweets())
        print "\n"


if __name__ == '__main__':

    n = raw_input('Enter the time window n (in minutes): ')

    #Handles Twitter authentication and connection to Twitter Streaming API
    l = retweetListener(n)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    stream.sample()