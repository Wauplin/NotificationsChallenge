import streamlit as st
from dashboard.st_utils.write_md import write_md


def conclusion():
    write_md('doc/conclusion.md')
