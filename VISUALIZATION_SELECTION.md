# Step 3: Visualization Selection

Each visualization was chosen to match the data type and the analytical question. All charts are built with **Plotly** so they are interactive (hover, zoom, filter) inside the Streamlit dashboard.

## Selected Visualizations

| Viz | Question                        | Technique                                                                                       | Plotly Implementation                        | Interactivity                                    |
| --- | ------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------ |
| V1  | Q1: Peak activity times         | **Heatmap** (weekday × hour)                                                                    | `px.density_heatmap` / `go.Heatmap`          | Hover for exact message count; date-range filter |
| V2  | Q2: Activity over time          | **Time-series line chart** + 7-day rolling average                                              | `px.line` / `go.Scatter`                     | Range slider, zoom, hover on spike days          |
| V3  | Q3: Activity distribution       | **Histogram** (log scale) + **box plot** + **top-10 bar chart**                                 | `px.histogram`, `px.box`, `px.bar`           | Min-messages filter; hover for user ID and count |
| V4  | Q4: Influential users           | **Network graph** (top-N users) + **scatter plot** (in-degree vs out-degree, sized by PageRank) | NetworkX layout + `go.Scatter`; `px.scatter` | Top-N selector; hover for degree and PageRank    |
| V5  | Q5: Reciprocity and reply speed | **Histogram** (log x-axis) + reciprocity KPI                                                    | `px.histogram(log_x=True)` + `st.metric`     | Date-range filter                                |

## Why These Techniques

- **Heatmap (V1):** two categorical time axes and one intensity measure; no other chart shows this as compactly.
- **Line chart (V2):** time is continuous and ordered, so a line shows trend and spikes best.
- **Histogram + box plot (V3):** the histogram shows the shape of the heavy-tailed distribution, and the box plot marks outliers explicitly.
- **Network graph + scatter (V4):** the graph shows structure, while the scatter compares in-degree and out-degree numerically, which a graph cannot do precisely.
- **Log-scale histogram (V5):** reply times range from seconds to days, so a linear axis would hide most of the data.

## Techniques Considered but Not Used

| Technique               | Reason for Not Using                                                                                                    |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Pair plot / Facet grid  | The dataset has only three raw attributes, so there are too few numeric variables to compare in pairs.                  |
| Choropleth / Folium map | No geographical variable in the dataset.                                                                                |
| Treemap / Sunburst      | No hierarchical categories (e.g. departments or groups) exist.                                                          |
| Pie chart               | Too many users and a heavy-tailed distribution make slices unreadable (used only in the Wrong Visualization Challenge). |

## Preprocessing Applied Before Plotting

- Removed 37 duplicate rows (59,798 records remain)
- Converted Unix timestamps to datetime and derived date, hour, and weekday
- Derived per-user variables: messages sent, messages received, in-degree, out-degree, PageRank
- Derived reply time for reciprocated message pairs
