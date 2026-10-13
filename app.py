"""Data Detective Challenge - CollegeMsg interactive dashboard (Streamlit + Plotly).
Run:  streamlit run app.py
Needs visualizations.py and CollegeMsg.txt.gz in the same folder.
"""
import os
import pandas as pd
import streamlit as st
import visualizations as viz

st.set_page_config(page_title="CollegeMsg Data Detective", layout="wide")
DATA_FILE = "CollegeMsg.txt.gz"


# ---------------------------------------------------------------- cache ----
@st.cache_data
def get_data(tz):
    return viz.load_data(DATA_FILE, tz=None if tz == "UTC" else tz)


@st.cache_data
def get_stats(df):
    return viz.user_stats(df)


@st.cache_data
def get_replies(df):
    return viz.reply_times(df)


if not os.path.exists(DATA_FILE):
    st.error(f"{DATA_FILE} not found. Download it from SNAP and place it next to app.py.")
    st.stop()

# ---------------------------------------------------------------- header ---
st.title("CollegeMsg Data Detective: Who talks, when, and to whom?")
st.markdown(
    "**Objective:** analyse a temporal social network to understand when users are active, "
    "how activity is distributed, who the key users are, and whether conversations are reciprocated."
)
with st.expander("Dataset / problem description"):
    st.markdown(
        "**Source:** SNAP *CollegeMsg*, private messages on an online social platform for "
        "college students (Apr to Oct 2004). Each record is one directed message with a sender, "
        "a receiver, and a Unix timestamp. Duplicate rows were removed during loading. "
        "**Problem:** with only three raw attributes, we derive time, degree, PageRank and "
        "reply-time variables to uncover community behaviour."
    )

# --------------------------------------------------------------- sidebar ---
st.sidebar.header("Filters")
tz = st.sidebar.selectbox("Timezone for hour/weekday", ["UTC", "US/Eastern", "US/Pacific"])
df_all = get_data(tz)

dmin, dmax = df_all["date"].min().date(), df_all["date"].max().date()
picked = st.sidebar.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
start, end = (picked[0], picked[1]) if isinstance(picked, (tuple, list)) and len(picked) == 2 else (dmin, dmax)

min_sent = st.sidebar.slider("Minimum messages sent per user", 0, 100, 0)
top_n = st.sidebar.slider("Top-N users in network graph", 10, 100, 50, step=10)

df = df_all[(df_all["date"] >= pd.Timestamp(start)) & (df_all["date"] <= pd.Timestamp(end))]
if min_sent > 0:
    counts = df["source"].value_counts()
    df = df[df["source"].isin(counts[counts >= min_sent].index)]
if df.empty:
    st.warning("No data for the selected filters. Widen the date range or lower the minimum.")
    st.stop()

stats = get_stats(df)

# ------------------------------------------------------------------ KPIs ---
st.subheader("Key Performance Indicators")
cols = st.columns(5)
for col, (label, value) in zip(cols, viz.kpis(df).items()):
    col.metric(label, f"{value:,}" if isinstance(value, int) else value)

# ---------------------------------------------------------------- charts ---
st.subheader("Analytical Visualizations")
c1, c2 = st.columns(2)
c1.plotly_chart(viz.fig_heatmap(df))
c2.plotly_chart(viz.fig_timeseries(df))

st.markdown("##### Activity distribution")
d1, d2, d3 = st.columns(3)
d1.plotly_chart(viz.fig_distribution(stats))
d2.plotly_chart(viz.fig_box(stats))
d3.plotly_chart(viz.fig_top_users(stats))

st.markdown("##### Influence and network structure")
n1, n2 = st.columns(2)
n1.plotly_chart(viz.fig_scatter(stats))
n2.plotly_chart(viz.fig_network(df, stats, top_n=top_n))

st.markdown("##### Reciprocity and reply speed")
replies = get_replies(df)
if len(replies):
    st.plotly_chart(viz.fig_reply_hist(df))
else:
    st.info("Not enough reciprocated messages in this selection to show reply times.")

# -------------------------------------------------------------- findings ---
st.subheader("Five Major Findings (computed from the current filters)")
senders = stats[stats["sent"] > 0].sort_values("sent", ascending=False)
k = max(1, int(0.1 * len(senders)))
share = senders.head(k)["sent"].sum() / senders["sent"].sum()
busy_hour = int(df["hour"].value_counts().idxmax())
busy_day = df["weekday"].astype(str).value_counts().idxmax()
daily = df.groupby("date").size()
spike_date, spike_val = daily.idxmax().date(), int(daily.max())

st.markdown(f"1. **Activity is concentrated:** the top 10% of senders ({k:,} users) account for "
            f"**{share:.0%}** of all messages sent.")
st.markdown(f"2. **Clear daily rhythm:** activity peaks at hour **{busy_hour}** ({tz}) and on **{busy_day}**.")
st.markdown(f"3. **One-off spike:** the busiest day was **{spike_date}** with **{spike_val:,}** messages, "
            f"**{spike_val / daily.mean():.1f}x** the daily average of {daily.mean():.0f}.")
st.markdown(f"4. **Most links are two-way:** **{100 * viz.reciprocity(df):.1f}%** of sender-receiver "
            f"pairs have a message in the reverse direction.")
if len(replies):
    st.markdown(f"5. **Replies are quick for many, slow for some:** among messages that got a reply, the "
                f"median reply time is **{replies.median():.1f} hours**, and **{(replies <= 1).mean():.0%}** "
                f"are answered within an hour.")
else:
    st.markdown("5. Reply-time finding unavailable for this selection.")

# -------------------------------------------------------- recommendations ---
st.subheader("Three Actionable Recommendations")
st.markdown(
    "1. **Engage the hubs:** a small group of users drives most traffic, so involve them as community "
    "ambassadors or early testers of new features.\n"
    "2. **Time announcements to peak hours:** schedule notifications, events and moderation staffing "
    "around the peak hours and weekdays in the heatmap.\n"
    "3. **Nudge unanswered messages:** reminders or prompts for messages without a reply can raise "
    "reciprocity and keep casual users engaged."
)
st.caption("Edit the wording of findings and recommendations to match your team's own interpretation "
           "after you review the charts.")