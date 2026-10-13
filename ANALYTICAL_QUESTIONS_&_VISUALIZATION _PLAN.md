# Step 2: Analytical Questions and Visualization Plan

| #   | Analytical Question                                                                                   | Variables Required                                                       | Proposed Visualization                                                                            | Why Is This Visualization Appropriate?                                                                                                                                               |
| --- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Q1  | At what hours of the day and days of the week are users most active?                                  | `timestamp` → weekday, hour; message count                               | **Heatmap** (weekday × hour)                                                                      | Two categorical time dimensions plus one intensity value is what a heatmap shows best. Peak and quiet periods stand out immediately through colour.                                  |
| Q2  | How does messaging activity change over the 193-day period, and what caused the spike on 27 May 2004? | `timestamp` → date; daily message count; daily active users              | **Time-series line chart** with 7-day rolling average and date-range slider                       | Continuous time data calls for a line chart. The rolling average separates the long-term trend from noise, and the slider lets viewers zoom into the spike.                          |
| Q3  | How is activity distributed across users? Do a few users dominate the traffic?                        | Messages sent per user; messages received per user                       | **Histogram** (log scale), **box plot**, and top-10 **bar chart**                                 | The histogram shows the shape of the distribution, the box plot flags outliers (159 outlier senders), and the bar chart names the heaviest users. Together they show the heavy tail. |
| Q4  | Who are the most influential users in the network?                                                    | Out-degree, in-degree, PageRank (derived with NetworkX)                  | **Network graph** (top-N users) and **scatter plot** (in-degree vs out-degree, sized by PageRank) | The graph shows hubs and connection structure. The scatter separates broadcasters (high out-degree) from popular receivers (high in-degree), which a graph alone can't do cleanly.   |
| Q5  | Are messages reciprocated, and how quickly do users reply?                                            | Sender-receiver pairs; timestamps; derived: reciprocity flag, reply time | **Histogram** (log x-axis) of reply times, plus a **reciprocity KPI**                             | Reply times are highly skewed, so a log axis reveals both fast replies and long gaps. The KPI (63.6% of pairs reciprocated) gives the headline number.                               |

## Planned Dashboard Controls

- **Date-range slider** (filters Q1 to Q5)
- **Minimum messages per user** (filters outliers and noise)
- **Top-N selector** for the network graph (e.g. 10 to 100 users)

## Planned KPIs

Total messages, unique users, unique connections, average messages per user, reciprocity %
