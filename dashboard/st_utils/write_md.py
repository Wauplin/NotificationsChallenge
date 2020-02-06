import streamlit as st
from pathlib import Path


def write_md(md_path):
    if not isinstance(md_path, Path):
        md_path = Path(md_path)
    with md_path.open() as f:
        st.write(f.read())
