import streamlit as st
from dashboard.st_utils.write_md import write_md


def challenge_presentation():
    write_md('doc/summary.md')
