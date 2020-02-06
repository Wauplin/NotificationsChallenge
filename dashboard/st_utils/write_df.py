import streamlit as st
from constants import DF_STREAMLIT_LIMIT


def write_df(title, df):
    st.write(f'### {title}')
    data = df.head(DF_STREAMLIT_LIMIT).copy()
    for col in data.columns:
        if str(data[col] == 'category'):
            data[col] = data[col].astype('str')
    st.write(data)
