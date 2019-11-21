# Mining Twitter with tweepy
# Adapted from code by Dr. Matthias Buehlmaier

# Set the source of the tweets
# User              Twitter ID
# CoinDesk          @coindesk
# Bitcoin News      @BTCTN
# Bloomberg Crypto  @crypto
# Bitcoin News      @Bitcoin
# Bitcoin Magazine  @BitcoinMagazine
# Bitcoin Forum     @BitcoinForumCom
# /r/Bitcoin        @RedditBTC
screen_name = "coindesk"

# Set up twitter API login information
# from your twitter developer account portal
# https://developer.twitter.com/

access_token = "xxx"
access_token_secret = "xxx"
consumer_key = "xxx"
consumer_secret = "xxx"

# Import tweepy and csv.
import tweepy
import csv

# Authorisation
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Initialize a list to hold all the tweets.
alltweets = []
# Make initial request for most recent tweets (200 is the maximum allowed count).
new_tweets = api.user_timeline(
    screen_name=screen_name, count=200, exclude_replies=True
)  # if no 'exclude_replies' default is false
# Save most recent tweets to the list.
alltweets.extend(new_tweets)
# Save the id of the oldest tweet less one.
oldest = alltweets[-1].id - 1
# Keep grabbing tweets until there are no tweets left to grab.
while len(new_tweets) > 0:
    print("getting tweets before %s" % oldest)
    # All subsequent requests use the max_id param to prevent duplicates.
    new_tweets = api.user_timeline(
        screen_name=screen_name, count=200, exclude_replies=True, max_id=oldest
    )
    # Save most recent tweets.
    alltweets.extend(new_tweets)
    # Update the id of the oldest tweet less one.
    oldest = alltweets[-1].id - 1
    print("...%s tweets downloaded so far" % len(alltweets))

# Use list comprehension to transform the tweets into a 2D array
# (list of row objects) that will populate the CSV file.
outtweets = [
    [tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets
]

# Write to CSV file.
with open(
    "data-%s-tweets-replies-excluded.csv" % screen_name, "w", encoding="utf-8"
) as f:
    writer = csv.writer(f)
    writer.writerow(["id", "created_at", "text"])
    writer.writerows(outtweets)
