# This creates the page for users to input data.
# The collected data is appended to the 'data.csv' file.

import csv
from pathlib import Path

import pandas as pd
import streamlit as st

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Survey",
    page_icon="📝",
)

# The CSV lives one folder above /pages. Building the path from this file's
# location means it works no matter which folder the app is launched from.
CSV_PATH = Path(__file__).resolve().parent.parent / "data.csv"
HEADER = ["Category", "Value"]
MAX_HOURS = 168  # hours in a week


def append_row(category, value):
    """Append one row to data.csv (writes the header first if the file is empty)."""
    file_has_data = CSV_PATH.exists() and CSV_PATH.stat().st_size > 0

    # If the last line of the file has no newline, add one so rows don't merge.
    needs_newline = False
    if file_has_data:
        with open(CSV_PATH, "rb") as f:
            f.seek(-1, 2)
            needs_newline = f.read(1) != b"\n"

    with open(CSV_PATH, "a", newline="") as f:
        if needs_newline:
            f.write("\n")
        writer = csv.writer(f, lineterminator="\n")  # handles commas/quotes safely
        if not file_has_data:
            writer.writerow(HEADER)
        writer.writerow([category, value])


# PAGE TITLE AND USER DIRECTIONS
st.title("Study Spot Survey 📝")
st.write(
    "Tell us where you usually study and how long you spend there. "
    "Your answer is added to the dataset used on the Visuals page."
)

# DATA INPUT FORM
with st.form("survey_form", clear_on_submit=True):
    category_input = st.text_input(
        "Where do you usually study? (e.g., Library, Dorm, Student Center)"
    )
    value_input = st.text_input(
        "About how many hours per week do you study there? (e.g., 6 or 7.5)"
    )

    submitted = st.form_submit_button("Submit Data")

    if submitted:
        category = " ".join(category_input.split()).title()  # tidy spacing/capitalization
        value_text = value_input.strip()

        # Validate the text the user typed before writing anything.
        try:
            hours = float(value_text)
        except ValueError:
            hours = None

        if not category:
            st.error("Please enter a study spot.")
        elif hours is None:
            st.error("Please enter the hours as a number, like 6 or 7.5.")
        elif not 0 < hours <= MAX_HOURS:
            st.error(f"Hours must be greater than 0 and at most {MAX_HOURS}.")
        else:
            hours_clean = int(hours) if hours == int(hours) else round(hours, 2)
            append_row(category, hours_clean)
            st.success("Your data has been submitted!")
            st.write(f"You entered: **Study spot:** {category}, **Hours/week:** {hours_clean}")


# DATA DISPLAY
st.divider()
st.header("Current Data in CSV")

if CSV_PATH.exists() and CSV_PATH.stat().st_size > 0:
    current_data_df = pd.read_csv(CSV_PATH)
    st.dataframe(current_data_df, use_container_width=True)
    st.caption(f"{len(current_data_df)} responses so far.")
else:
    st.warning("The 'data.csv' file is empty or does not exist yet.")
