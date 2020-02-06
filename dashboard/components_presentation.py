import streamlit as st

from dashboard.st_utils.write_md import write_md


def components_presentation():
    write_md('doc/components_presentation.md')
