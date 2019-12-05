# Code by Dominic Yuen
import pandas as pd
import numpy as np
from math import sqrt

price = pd.read_csv("Coinbase_BTCUSD_1h.csv")
price.sort_values(by="Date", inplace=True)
price["Date"] = pd.to_datetime(price["Date"], format=r"%Y-%m-%d %I-%p")

ts = pd.read_csv("rf-bow-test.csv", names=["Date", "score"])
ts["Date"] = pd.to_datetime(ts["Date"])

df = pd.merge(ts, price)
df.dropna(inplace=True)

# input the variableto backtest (sum: bound = 12, step = 0.1; avg: bound = 0.6, step = 0.01)
score = "score"
bound = 1
step = 0.01

# dataframe and other variables setup
df = df.fillna(method="ffill").dropna()
df["p_%chg"] = df["Close"].pct_change()
df.dropna(inplace=True)
res = []

# input transaction costs
tc = 10/(8500*5)

# optimizer
for i in np.arange(0, bound, step):
    try:
        df["posi"] = np.where(df[score] > i, 1, np.where(df[score] < i, -1, 0))
        df["pnl"] = df["posi"].shift(1) * df["p_%chg"] - abs(df["posi"].diff()) * tc
        sr_is = df["pnl"].iloc[:268].mean() / df["pnl"].iloc[:268].std() * sqrt(252)
        sr_os = df["pnl"].iloc[268:].mean() / df["pnl"].iloc[268:].std() * sqrt(252)
        res.append([sr_is, sr_os, i])

    except:
        res.append(["math error", "math error", "math error", i])

opt = pd.DataFrame(res)
opt.columns = ["sr_is", "sr_os", "thres"]
opt = opt.sort_values(by="sr_is", ascending=False)
print(opt.head())

# optimized result plotting
thres = opt["thres"].iloc[0]
df["posi"] = np.where(df[score] > thres, 1, np.where(df[score] < thres, -1, 0))
df["pnl"] = df["posi"].shift(1) * df["p_%chg"] - abs(df["posi"].diff()) * tc
df["cpnl"] = df["pnl"].cumsum()
df["cpnl"].plot()