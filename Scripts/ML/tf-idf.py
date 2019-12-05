from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier

df = pd.read_parquet(
    "/home/noel/Desktop/tokens.parquet", columns=["time", "cleaned"], engine="pyarrow",
)
df.dropna(inplace=True)

df["date"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
df.dropna(inplace=True)
df["date"] = df["date"].dt.floor("H")

# Price
price = pd.read_csv("~/Desktop/Coinbase_BTCUSD_1h.csv")
price["Date"] = pd.to_datetime(price["Date"], format=r"%Y-%m-%d %I-%p")
price.sort_values(by="Date", inplace=True)

price["nClose"] = price["Close"].shift(-1)
price["Return"] = price["nClose"] / price["Close"] - 1
price.dropna(inplace=True)

price["cat"] = np.where(price["Return"] > 0, 1, 0)

ret = price[["Date", "cat"]].copy()
ret.columns = ["date", "ret"]
del price

df = pd.merge(df, ret, on="date")
df.dropna(inplace=True)


def dummy(x):
    return x


cv = TfidfVectorizer(tokenizer=dummy, lowercase=False, preprocessor=dummy, min_df=100)

tfidf = cv.fit_transform(df["cleaned"])

# Split Train/Test Sets
X_train, X_test, y_train, y_test = train_test_split(
    tfidf, df, test_size=0.33, random_state=42
)

# NB
print("Naive Bayes")
nb = MultinomialNB()
nb.fit(X_train, y_train.ret)

nb_res = nb.predict(X_test)
print(classification_report(y_test.ret, nb_res))

# XGB
print("XGBoost")
model = XGBClassifier()
model.fit(X_train, y_train.ret)

xgb_res = model.predict(X_test)
print(classification_report(y_test.ret, xgb_res))

# Logistic Regression
print("Logistic Regression")
lr = LogisticRegression(solver="saga")
lr.fit(X_train, y_train.ret)

lr_res = lr.predict(X_test)
print(classification_report(y_test.ret, lr_res))

# Support Vector Machine
print("Support Vector Machine")
svm = LinearSVC()
svm.fit(X_train, y_train.ret)

svm_res = svm.predict(X_test)
print(classification_report(y_test.ret, svm_res))

# Random Forest
print("Random Forest")
rf = RandomForestClassifier()
rf.fit(X_train, y_train.ret)

rf_res = rf.predict(X_test)
print(classification_report(y_test.ret, rf_res))

# Average Score per Hour
y_test["predicted"] = rf.predict(X_test)
gr = y_test.groupby("date")["predicted"].mean()
gr.to_csv("rf-tfidf-test.csv")
