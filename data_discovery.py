"""Step 1 - Dataset Discovery for CollegeMsg (SNAP).
Download CollegeMsg.txt.gz from https://snap.stanford.edu/data/CollegeMsg.html
and put it next to this script. Run: python step1_discovery.py
"""
import pandas as pd
import numpy as np

# ---- Load -------------------------------------------------------------
df = pd.read_csv(
    "CollegeMsg.txt.gz", sep=" ", header=None,
    names=["source", "target", "timestamp"],
)
df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
df["date"] = df["datetime"].dt.date
df["hour"] = df["datetime"].dt.hour
df["weekday"] = df["datetime"].dt.day_name()

print("=== 1. SHAPE & TYPES ===")
print("Records (messages):", len(df))
print("Raw attributes:", list(df.columns[:3]))
print(df.dtypes, "\n")

print("=== 2. USERS & CONNECTIONS ===")
users = pd.concat([df["source"], df["target"]]).nunique()
print("Unique users:", users)
print("Unique senders:", df["source"].nunique())
print("Unique receivers:", df["target"].nunique())
pairs = df[["source", "target"]].drop_duplicates()
print("Unique directed sender->receiver pairs:", len(pairs), "\n")

print("=== 3. TEMPORAL RANGE ===")
print("Start:", df["datetime"].min())
print("End:  ", df["datetime"].max())
print("Span (days):", (df["datetime"].max() - df["datetime"].min()).days)
print("Active days:", df["date"].nunique(), "\n")

print("=== 4. MISSING / DUPLICATES / ANOMALIES ===")
print("Missing values per column:\n", df[["source", "target", "timestamp"]].isna().sum())
print("Fully duplicate rows:", df.duplicated(["source", "target", "timestamp"]).sum())
print("Self-messages (source == target):", (df["source"] == df["target"]).sum())
print("Timestamps out of order:", (df["timestamp"].diff().dropna() < 0).sum(), "\n")

print("=== 5. DERIVED NUMERICAL VARIABLES ===")
sent = df.groupby("source").size().rename("sent")
recv = df.groupby("target").size().rename("received")
user_stats = pd.concat([sent, recv], axis=1).fillna(0)
user_stats["total"] = user_stats["sent"] + user_stats["received"]
print(user_stats.describe().round(2), "\n")

print("=== 6. OUTLIERS (IQR rule on messages sent) ===")
q1, q3 = sent.quantile([0.25, 0.75])
upper = q3 + 1.5 * (q3 - q1)
outliers = sent[sent > upper]
print(f"Upper fence: {upper:.1f}; outlier senders: {len(outliers)} "
      f"({len(outliers) / len(sent):.1%})")
print("Top 5 senders:\n", sent.sort_values(ascending=False).head(5), "\n")

print("=== 7. QUICK PATTERNS ===")
print("Busiest hour:", df["hour"].value_counts().idxmax())
print("Busiest weekday:", df["weekday"].value_counts().idxmax())
daily = df.groupby("date").size()
print("Daily messages: mean %.1f, max %d on %s" % (daily.mean(), daily.max(), daily.idxmax()))
rev = set(zip(pairs["target"], pairs["source"]))
recip = sum((s, t) in rev for s, t in zip(pairs["source"], pairs["target"]))
print("Pairs with reciprocated messages: %.1f%%" % (100 * recip / len(pairs)))