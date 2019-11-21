# Adapted from code by Shikhar Chauhan
# https://medium.com/mindorks/speeding-up-text-pre-processing-using-dask-45cc3ede1366

import dask.dataframe as dd
import nltk
import pandas as pd
import spacy

df = dd.read_parquet("tweets.parquet", columns=["timestamp", "text"], engine="pyarrow",)


def tokenize(text):
    """
    Tokenize text
    """
    tokens = nltk.word_tokenize(text)

    return list(filter(lambda word: word.isalnum(), tokens))


stop_words = nltk.corpus.stopwords.words("english")
stop_words.extend(["bitcoin", "btc", "http", "https"])


def remove_stopwords(words):
    """
    Remove stop words from the list of words
    """

    filtered = filter(lambda word: word not in stop_words, words)

    return list(filtered)


nlp = spacy.load("en_core_web_sm")


def lemmatize(text, nlp=nlp):

    doc = nlp(" ".join(text))

    lemmatized = [token.lemma_ for token in doc]

    return lemmatized


def clean_text(df):
    """
    Take in a Dataframe, and process it
    """
    df["cleaned"] = (
        df.text.map(lambda x: str(x).lower())
        .map(tokenize)
        .map(remove_stopwords)
        .map(lemmatize)
    )
    return df


tokens = df.map_partitions(clean_text).compute()
tokens.to_parquet("tokens.parquet", engine="pyarrow")
