# Dataset from https://www.kaggle.com/alaix14/bitcoin-tweets-20160101-to-20190329

import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

df = pd.read_parquet(
    "tokens.parquet", columns=["timestamp", "cleaned"], engine="pyarrow",
)
df.dropna(inplace=True)

df["datetime"] = pd.to_datetime(
    df["timestamp"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
)
df.dropna(inplace=True)
# Uncomment to adjust time zone
# df["datetime"] = df["datetime"].dt.tz_localize("UTC")
# df["datetime"] = df["datetime"].dt.tz_convert("America/Chicago")
df["date"] = df["datetime"].dt.date.astype(str)

# Categories tweets into short, do nothing and long (-1, 0 , 1)
# Based on percentage change of returns
# Adapted from code by Dr. Matthias Buehlmaier
price = pd.read_csv("BTC-USD.csv")
price.sort_values(by="Date", inplace=True)
price.reset_index(drop=True, inplace=True)
price["Date"] = pd.to_datetime(price["Date"]).dt.date

price["lagClose"] = price["Close"].shift()
price["Return"] = price["Close"] / price["lagClose"] - 1
price["lagReturn"] = price["Return"].shift(-1)
price.dropna(inplace=True)

price["cat"] = 0
pd.options.mode.chained_assignment = None  # Disable SettingWithCopyWarning
price["cat"][price.lagReturn > 0.01] = 1
price["cat"][price.lagReturn < -0.01] = -1
pd.options.mode.chained_assignment = "warn"  # Enable SettingWithCopyWarning

ret = price[["Date", "cat"]].copy()
ret.columns = ["date", "ret"]
del price

drange = pd.DataFrame(
    pd.date_range(ret["date"].min(), ret["date"].max()), columns=["date"]
)
drange["date"] = drange.date.astype(str)
ret["date"] = ret.date.astype(str)

ret = pd.merge(drange, ret, how="left", left_on="date", right_on="date").fillna(
    method="bfill"
)

df = pd.merge(df, ret, how="left", left_on="date", right_on="date")

# Create Tf-idf
def rm_num(l):
    # Removes tokens with digits
    return [x for x in l if not any(y.isdigit() for y in x)]


def dummy(x):
    # Dummy function to disable the preprocessor of TfidfVectorizer
    return x


cv = TfidfVectorizer(tokenizer=rm_num, lowercase=False, preprocessor=dummy, min_df=100)
tfidf = cv.fit_transform(df["cleaned"])

joblib.dump(cv, "tfidf.pkl")

# Split Train/Test Sets
X_train, X_test, y_train, y_test = train_test_split(
    tfidf, df, test_size=0.33, random_state=42
)

# Naive Bayes Machine Learning

nb = MultinomialNB()
nb.fit(X_train, y_train.ret)

nb_res = nb.predict(X_test)
print("Naive Bayes Result:\n")
print(classification_report(y_test.ret, nb_res))

joblib.dump(nb, "nb.pkl")

# XGBoost Machine Learning

xgb = XGBClassifier()
xgb.fit(X_train, y_train.ret)

xgb_res = xgb.predict(X_test)
print("\nXGBoost Result:\n")
print(classification_report(y_test.ret, xgb_res))

joblib.dump(xgb, "xgb.pkl")
