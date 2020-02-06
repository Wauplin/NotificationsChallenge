import streamlit as st
from dashboard.st_utils.write_md import write_md


def challenge_presentation():
    st.title('Summary')
    write_md('doc/summary.md')
    st.title('Readme')
    write_md('README.md')
