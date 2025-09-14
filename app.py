# app.py
import streamlit as st
from ui.layout import sidebar_inputs, main_tabs

APP_TITLE = "AI Cover Letter Builder — Modular"
APP_INTRO = (
    "Generate an ATS-friendly, tailored cover letter from a job ad and your profile. "
    "This modular version splits logic across packages for easier maintenance and extension."
)

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="📝", layout="wide")
    st.title(APP_TITLE)
    st.write(APP_INTRO)

    with st.sidebar:
        state = sidebar_inputs()

    main_tabs(state)

if __name__ == "__main__":
    main()