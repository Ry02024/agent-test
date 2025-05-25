# This will be the main page of the Streamlit application.
# Streamlit will automatically pick this up if named correctly and placed in a 'pages' directory.
# For now, it can be empty or contain a simple Streamlit title.

import streamlit as st

# st.set_page_config(layout="wide", page_title="Home") # Example config

def show_home_page():
    st.title("Home Page")
    st.write("Welcome to the home page!")

if __name__ == "__main__":
    show_home_page()
