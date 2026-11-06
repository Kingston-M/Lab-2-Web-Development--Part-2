# This creates the page for displaying data visualizations.
# Part 1 uses data.json, Part 2 uses data.csv.

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Visuals",
    page_icon="📈",
)

# Build file paths from this file's location so the app works wherever it is launched.
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "data.json"
CSV_PATH = BASE_DIR / "data.csv"


def track_stats(prefix, signature, mean, median):
    """Use session state to remember the previous mean/median.

    `signature` describes the current widget choices. Only when it changes do we
    move the old stats into '<prefix>_prev'. That way st.metric can show how the
    numbers changed, and a plain page rerun doesn't wipe out the comparison.
    Returns the previous (mean, median) tuple, or None on the first view.
    """
    if st.session_state.get(f"{prefix}_sig") != signature:
        if f"{prefix}_stats" in st.session_state:
            st.session_state[f"{prefix}_prev"] = st.session_state[f"{prefix}_stats"]
        st.session_state[f"{prefix}_sig"] = signature
        st.session_state[f"{prefix}_stats"] = (mean, median)
    return st.session_state.get(f"{prefix}_prev")


def show_metrics(prefix, signature, values, unit):
    """Show mean and median with st.metric, including change since the last interaction."""
    mean, median = float(values.mean()), float(values.median())
    prev = track_stats(prefix, signature, mean, median)
    col1, col2 = st.columns(2)
    col1.metric(
        "Mean",
        f"{mean:.2f} {unit}".strip(),
        delta=None if prev is None else round(mean - prev[0], 2),
    )
    col2.metric(
        "Median",
        f"{median:.2f} {unit}".strip(),
        delta=None if prev is None else round(median - prev[1], 2),
    )


# PAGE TITLE
st.title("Data Visualizations 📈")


# =====================================================================
# PART 1: GRAPHS FROM data.json
# =====================================================================
st.header("Part 1: My Weekly Time Log (data.json)")

try:
    with open(JSON_PATH) as f:
        json_data = json.load(f)
    json_df = pd.DataFrame(json_data["data_points"])
    activities = json_data["activities"]
    json_title = json_data["chart_title"]
    json_unit = json_data["unit"]
except (OSError, json.JSONDecodeError, KeyError) as error:
    st.error(f"Could not load data.json: {error}")
    st.stop()

with st.expander("Show the raw JSON data"):
    st.json(json_data)

# ---- Static visualization (Matplotlib pie chart) ----
st.subheader("Where does my week go? (static)")
totals = json_df[activities].sum()

fig1, ax1 = plt.subplots(figsize=(6, 5))
wedges, _texts, _autotexts = ax1.pie(
    totals,
    labels=totals.index,
    autopct="%1.1f%%",
    startangle=90,
    wedgeprops={"edgecolor": "white"},
)
ax1.set_title(f"Share of Logged Hours by Activity\n({json_title})")
ax1.legend(
    wedges,
    [f"{name}: {hours:g} {json_unit}" for name, hours in totals.items()],
    title="Total for the week",
    loc="center left",
    bbox_to_anchor=(1, 0.5),
)
ax1.axis("equal")
fig1.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

# ---- Dynamic visualization (Matplotlib line chart) ----
st.subheader("Explore one activity day by day (dynamic)")
day_labels = json_df["label"].tolist()

chosen_activity = st.radio(
    "Choose an activity:", activities, horizontal=True, key="p1_activity"
)
first_day, last_day = st.select_slider(
    "Choose a range of days:",
    options=day_labels,
    value=(day_labels[0], day_labels[-1]),
    key="p1_days",
)

start_i, end_i = day_labels.index(first_day), day_labels.index(last_day)
subset = json_df.iloc[start_i : end_i + 1]

fig2, ax2 = plt.subplots(figsize=(7, 4))
ax2.plot(subset["label"], subset[chosen_activity], marker="o", linewidth=2)
ax2.axhline(
    subset[chosen_activity].mean(), linestyle="--", color="gray", label="Mean of selection"
)
ax2.set_title(f"{chosen_activity} Hours per Day ({first_day} to {last_day})")
ax2.set_xlabel("Day of the week")
ax2.set_ylabel(f"Hours ({json_unit})")
ax2.set_ylim(bottom=0)
ax2.grid(alpha=0.3)
ax2.legend()
fig2.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

# Extra credit: mean/median that update as the chart changes
st.caption("Summary of the selected data (arrows show change from your previous selection):")
show_metrics(
    "p1",
    (chosen_activity, first_day, last_day),
    subset[chosen_activity],
    "hrs",
)

st.divider()

# =====================================================================
# PART 2: GRAPHS FROM data.csv
# =====================================================================
st.header("Part 2: Campus Study Spots (data.csv)")

try:
    csv_df = pd.read_csv(CSV_PATH)
    csv_df["Value"] = pd.to_numeric(csv_df["Value"], errors="coerce")
    csv_df = csv_df.dropna(subset=["Category", "Value"])
except (OSError, pd.errors.EmptyDataError, KeyError):
    csv_df = pd.DataFrame(columns=["Category", "Value"])

if csv_df.empty:
    st.info("No survey responses yet. Add some on the Survey page, then come back!")
    st.stop()

st.write(f"Based on **{len(csv_df)}** survey responses.")

# ---- Static visualization (Matplotlib bar chart) ----
st.subheader("Average weekly study hours by spot (static)")
avg_by_spot = csv_df.groupby("Category")["Value"].mean().sort_values(ascending=False)

fig3, ax3 = plt.subplots(figsize=(7, 4))
bars = ax3.bar(avg_by_spot.index, avg_by_spot.values, color="#B3A369", edgecolor="black")
ax3.bar_label(bars, fmt="%.1f", padding=2)
ax3.set_title("Average Weekly Study Hours by Study Spot")
ax3.set_xlabel("Study spot")
ax3.set_ylabel("Average hours per week")
ax3.tick_params(axis="x", rotation=30)
fig3.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

# ---- Dynamic visualization (Matplotlib pie chart) ----
st.subheader("Compare study spots (dynamic)")

metric_choice = st.selectbox(
    "What should the pie chart show?",
    ["Total hours", "Average hours", "Number of responses"],
    key="p2_metric",
)
max_hours = max(1, int(math.ceil(csv_df["Value"].max())))
min_hours = st.slider(
    "Only include responses of at least this many hours per week:",
    min_value=0,
    max_value=max_hours,
    value=0,
    key="p2_min_hours",
)

filtered = csv_df[csv_df["Value"] >= min_hours]

if filtered.empty:
    st.warning("No responses match that filter. Try lowering the minimum hours.")
else:
    grouped = filtered.groupby("Category")["Value"]
    if metric_choice == "Total hours":
        pie_values = grouped.sum()
    elif metric_choice == "Average hours":
        pie_values = grouped.mean()
    else:
        pie_values = grouped.count()

    fig4, ax4 = plt.subplots(figsize=(6, 5))
    wedges4, _t, _a = ax4.pie(
        pie_values,
        labels=pie_values.index,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": "white"},
    )
    ax4.set_title(f"{metric_choice} by Study Spot (responses of {min_hours}+ hrs/week)")
    ax4.legend(
        wedges4,
        [f"{name}: {val:.1f}" for name, val in pie_values.items()],
        title=metric_choice,
        loc="center left",
        bbox_to_anchor=(1, 0.5),
    )
    ax4.axis("equal")
    fig4.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)

    # Extra credit: mean/median of the plotted values, with change since last interaction
    st.caption(
        f"Mean and median of the {len(pie_values)} slices shown "
        "(arrows show change from your previous selection):"
    )
    show_metrics("p2", (metric_choice, min_hours), pie_values, "")
