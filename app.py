import code
import streamlit as st
from pathlib import Path

from dashboard.st_utils.login_page import LoginPage

from dashboard.challenge_presentation import challenge_presentation
from dashboard.data_exploration import data_exploration
from dashboard.components_presentation import components_presentation
from dashboard.interactive_tests import interactive_tests
from dashboard.solution import solution
from dashboard.conclusion import conclusion

with LoginPage() as session:
    if session:

        pages = {}  # Pages keys are ordered
        pages['Challenge presentation'] = challenge_presentation
        pages['Data exploration'] = data_exploration
        pages['Components presentation'] = components_presentation
        pages['Interactive tests'] = interactive_tests
        pages['Solution tool'] = solution
        pages['Conclusion'] = conclusion

        page = pages[st.sidebar.selectbox('Page', list(pages.keys()))]

        st.sidebar.markdown('---')

        if page is not None:
            page()
