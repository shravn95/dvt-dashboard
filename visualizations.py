"""Step 3 - Visualizations for CollegeMsg (Plotly).
Each fig_* function returns a Plotly figure, so the Streamlit dashboard can
reuse them with st.plotly_chart(fig).

Run directly to export every chart as an HTML file (for screenshots):
    python visualizations.py
Needs: pandas, numpy, plotly, networkx
"""
import numpy as np
import pandas as pd
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ---------------------------------------------------------------- data ----
def load_data(path="CollegeMsg.txt.gz", tz=None):
    """Load, remove duplicates, derive time columns.
    tz: optional timezone name (e.g. 'US/Pacific'); None keeps UTC."""
    df = pd.read_csv(path, sep=" ", header=None, names=["source", "target", "timestamp"])
    df = df.drop_duplicates().reset_index(drop=True)  # removes the 37 duplicate rows
    dt = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    if tz:
        dt = dt.dt.tz_convert(tz)
    df["datetime"] = dt.dt.tz_localize(None)
    df["date"] = df["datetime"].dt.normalize()
    df["hour"] = df["datetime"].dt.hour
    df["weekday"] = pd.Categorical(df["datetime"].dt.day_name(), WEEKDAYS, ordered=True)
    return df


def user_stats(df):
    """Per-user derived variables: sent, received, PageRank."""
    sent = df.groupby("source").size().rename("sent")
    recv = df.groupby("target").size().rename("received")
    stats = pd.concat([sent, recv], axis=1).fillna(0).astype(int)
    G = nx.from_pandas_edgelist(df.drop_duplicates(["source", "target"]),
                                "source", "target", create_using=nx.DiGraph)
    stats["pagerank"] = pd.Series(nx.pagerank(G)).reindex(stats.index).fillna(0)
    stats["total"] = stats["sent"] + stats["received"]
    return stats.rename_axis("user").reset_index()


def reply_times(df):
    """For each message A->B, time (hours) until the next B->A message.
    Messages that never get a reply are excluded."""
    left = df[["source", "target", "timestamp"]].sort_values("timestamp")
    right = left.rename(columns={"source": "r_source", "target": "r_target"})
    right["reply_ts"] = right["timestamp"]
    merged = pd.merge_asof(
        left, right, on="timestamp",
        left_by=["target", "source"], right_by=["r_source", "r_target"],
        direction="forward", allow_exact_matches=False,
    )
    hours = (merged["reply_ts"] - merged["timestamp"]).dropna() / 3600
    return hours[hours > 0]


def reciprocity(df):
    """Share of unique sender->receiver pairs that also exist in reverse."""
    pairs = df[["source", "target"]].drop_duplicates()
    rev = set(zip(pairs["target"], pairs["source"]))
    return sum((s, t) in rev for s, t in zip(pairs["source"], pairs["target"])) / len(pairs)


def kpis(df):
    pairs = df[["source", "target"]].drop_duplicates()
    users = pd.concat([df["source"], df["target"]]).nunique()
    return {
        "Total messages": len(df),
        "Unique users": users,
        "Unique connections": len(pairs),
        "Avg messages per user": round(len(df) / users, 1),
        "Reciprocity %": round(100 * reciprocity(df), 1),
    }


# ------------------------------------------------------------- Q1 / V1 ----
def fig_heatmap(df):
    grid = (df.groupby(["weekday", "hour"], observed=False).size()
              .unstack(fill_value=0).reindex(WEEKDAYS))
    fig = px.imshow(grid, aspect="auto", color_continuous_scale="YlOrRd",
                    labels=dict(x="Hour of day", y="Weekday", color="Messages"),
                    title="Q1: Messaging activity by weekday and hour")
    return fig


# ------------------------------------------------------------- Q2 / V2 ----
def fig_timeseries(df):
    daily = df.groupby("date").size().rename("messages").reset_index()
    daily["7-day average"] = daily["messages"].rolling(7, center=True, min_periods=1).mean()
    fig = go.Figure()
    fig.add_bar(x=daily["date"], y=daily["messages"], name="Daily messages", opacity=0.35)
    fig.add_scatter(x=daily["date"], y=daily["7-day average"], name="7-day average",
                    line=dict(width=3))
    fig.update_layout(title="Q2: Daily message volume", xaxis_title="Date",
                      yaxis_title="Messages", xaxis_rangeslider_visible=True)
    return fig


# ------------------------------------------------------------- Q3 / V3 ----
def fig_distribution(stats):
    sent = stats[stats["sent"] > 0]
    return px.histogram(sent, x="sent", nbins=60, log_y=True,
                        title="Q3: Messages sent per user (log scale)",
                        labels={"sent": "Messages sent", "count": "Users"})


def fig_box(stats):
    sent = stats[stats["sent"] > 0]
    return px.box(sent, x="sent", points="outliers", hover_data=["user"],
                  title="Q3: Spread and outliers of messages sent",
                  labels={"sent": "Messages sent"})


def fig_top_users(stats, n=10):
    top = stats.nlargest(n, "sent").copy()
    top["user"] = top["user"].astype(str)
    return px.bar(top, x="sent", y="user", orientation="h",
                  title=f"Q3: Top {n} senders",
                  labels={"sent": "Messages sent", "user": "User ID"}
                  ).update_yaxes(autorange="reversed")


# ------------------------------------------------------------- Q4 / V4 ----
def fig_scatter(stats):
    d = stats[stats["total"] > 0]
    return px.scatter(d, x="sent", y="received", size="pagerank", hover_name="user",
                      log_x=True, log_y=True, opacity=0.6,
                      title="Q4: Sent vs received (bubble size = PageRank)",
                      labels={"sent": "Messages sent (out-degree proxy)",
                              "received": "Messages received (in-degree proxy)"})


def fig_network(df, stats, top_n=50, seed=42):
    top = set(stats.nlargest(top_n, "pagerank")["user"])
    edges = (df[df["source"].isin(top) & df["target"].isin(top)]
             .groupby(["source", "target"]).size().rename("weight").reset_index())
    G = nx.from_pandas_edgelist(edges, "source", "target", "weight", create_using=nx.DiGraph)
    G.add_nodes_from(top)
    pos = nx.spring_layout(G, seed=seed, k=0.6)

    ex, ey = [], []
    for u, v in G.edges():
        ex += [pos[u][0], pos[v][0], None]
        ey += [pos[u][1], pos[v][1], None]
    pr = stats.set_index("user")["pagerank"]
    nodes = list(G.nodes())
    fig = go.Figure()
    fig.add_scatter(x=ex, y=ey, mode="lines", line=dict(width=0.4, color="#999"),
                    hoverinfo="none", name="messages")
    fig.add_scatter(x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes],
                    mode="markers", name="users",
                    marker=dict(size=[8 + 600 * pr[n] for n in nodes], color=[pr[n] for n in nodes],
                                colorscale="Viridis", showscale=True,
                                colorbar=dict(title="PageRank")),
                    text=[f"User {n}<br>PageRank {pr[n]:.4f}" for n in nodes], hoverinfo="text")
    fig.update_layout(title=f"Q4: Network of top {top_n} users by PageRank",
                      showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


# ------------------------------------------------------------- Q5 / V5 ----
def fig_reply_hist(df):
    hrs = reply_times(df)
    fig = px.histogram(x=hrs, nbins=80, log_x=True,
                       title="Q5: Time until reply (hours, log scale)",
                       labels={"x": "Reply time (hours)", "count": "Messages"})
    fig.update_layout(xaxis_title="Reply time (hours, log scale)", yaxis_title="Messages")
    return fig


# ---------------------------------------------------------------- main ----
if __name__ == "__main__":
    df = load_data()  # pass tz="US/Pacific" etc. to convert from UTC
    stats = user_stats(df)
    print(kpis(df))
    figs = {
        "q1_heatmap": fig_heatmap(df),
        "q2_timeseries": fig_timeseries(df),
        "q3_histogram": fig_distribution(stats),
        "q3_box": fig_box(stats),
        "q3_top_users": fig_top_users(stats),
        "q4_scatter": fig_scatter(stats),
        "q4_network": fig_network(df, stats, top_n=50),
        "q5_reply_hist": fig_reply_hist(df),
    }
    for name, fig in figs.items():
        fig.write_html(f"{name}.html")
        print("saved", f"{name}.html")