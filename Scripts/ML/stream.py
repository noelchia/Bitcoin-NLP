# This script shows how to stream only selected fields to a file. The
# fields are separated by ' : ' (i.e. space, colon, space) for easier
# parsing later on.
import tweepy
from pathlib import Path
import csv

home = str(Path.home())

# Here you need to set your Twitter API keys.
access_token = "xxx"
access_token_secret = "xxx"
consumer_key = "xxx"
consumer_secret = "xxx"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

class listener(tweepy.StreamListener):
    def on_status(self, status):
        with open(home + '/data-streaming-tweets.csv', 'a+', encoding='utf-8') as f:
            row = [status.user.screen_name, status.user.followers_count, status.created_at, status.text]
            writer = csv.writer(f)
            writer.writerow(row)
        return True
    
    def on_error(self, status_code):
        print(status_code)
def startStream():
	try:
		mystream = \
		    tweepy.Stream(
		        auth=api.auth,
		        listener=listener())
		mystream.filter(languages=["en"], track=['btc', 'bitcoin'])
	except Exception as ex:
		print(ex)
		startStream()

startStream()
