# This creates the main landing page for the Streamlit application.
# Contains an introduction to the project and guides users to other pages.

import streamlit as st

st.set_page_config(
    page_title="Homepage",
    page_icon="🏠",
)

# WELCOME PAGE TITLE
st.title("Study Habits Dashboard 📚")

# INTRODUCTORY TEXT
st.write("""
Welcome! This app explores how college students spend their time and
where they like to study. It combines two datasets:

- **My weekly time log** (stored in `data.json`): how many hours I spend
  each day on sleep, studying, the gym, and socializing.
- **Campus study-spot survey** (stored in `data.csv`): answers collected
  from visitors like you about where they study and for how long.

### How to use this app
- **Survey** (sidebar): tell us where you study and for how many hours a week.
  Your answer is saved to the CSV file right away.
- **Visuals** (sidebar): see the data as charts. Some charts are fixed, and
  others respond to the widgets you use (radio buttons, sliders, select boxes).
  The summary statistics next to each interactive chart update as you change things.

This project is part of CS 1301's Lab 2.
""")

st.info("Use the sidebar on the left to switch between pages.")
