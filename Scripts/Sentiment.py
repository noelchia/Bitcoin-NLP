import pandas as pd
import numpy as np
import nltk.sentiment.vader
import re

df = pd.read_csv("All_tweets_replies_excluded.csv")

# Separate Date and Time
df["created_at"] = pd.to_datetime(df.created_at)
df.insert(1, "created_on", df.created_at.dt.date)
df["created_at"] = df.created_at.dt.time

# Fix the encoding of text
df.dropna(inplace=True)
df["text"] = df["text"].apply(lambda x: eval(x.replace("\xa0", "")).decode("utf-8"))

# Clean Tweets
def remove_pattern(input_txt, pattern):
    # Adapted from Marcelo Rovai
    # https://towardsdatascience.com/almost-real-time-twitter-sentiment-analysis-with-tweep-vader-f88ed5b93b1c

    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, "", input_txt)
    return input_txt


def clean_tweets(lst):
    # Adapted from Marcelo Rovai
    # https://towardsdatascience.com/almost-real-time-twitter-sentiment-analysis-with-tweep-vader-f88ed5b93b1c

    # remove twitter Return handles (RT @xxx:)
    lst = np.vectorize(remove_pattern)(lst, "RT @[\w]*:")
    # remove twitter handles (@xxx)
    lst = np.vectorize(remove_pattern)(lst, "@[\w]*")
    # remove URL links (httpxxx)
    lst = np.vectorize(remove_pattern)(lst, "https?://[A-Za-z0-9./]*")
    # remove special characters, numbers, punctuations (except for #)
    lst = np.core.defchararray.replace(lst, "[^a-zA-Z#]", " ")
    return lst


df["text"] = clean_tweets(df["text"])

# Use Vader to obtain sentiment
sia = nltk.sentiment.vader.SentimentIntensityAnalyzer()
df["Sentiment"] = df["text"].apply(lambda x: sia.polarity_scores(x)["compound"])

# Write results to csv
df.to_csv("Sentiment.csv", index=None, header=True)
