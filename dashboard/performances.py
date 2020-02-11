import streamlit as st
from dashboard.st_utils.write_md import write_md


def performances():
    write_md('doc/performances.md')
