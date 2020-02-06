"""
Taken from https://raw.githubusercontent.com/MarcSkovMadsen/awesome-streamlit/master/gallery/file_download/file_download.py

There is currently (20191204) no official way of downloading data from Streamlit. See for
example [Issue 400](https://github.com/streamlit/streamlit/issues/400)

But I discovered a workaround
[here](https://github.com/holoviz/panel/issues/839#issuecomment-561538340).

It's based on the concept of
[HTML Data URLs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs)

You can try it out below for a dataframe csv file download.

The methodology can be extended to other file types. For inspiration see
[base64.guru](https://base64.guru/converter/encode/file)
"""

import base64
import pandas as pd
import streamlit as st


def file_download(df, name='&lt;some_name&gt;'):
    csv = df.head(1000).to_csv(index=False)
    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as {name}.csv). Contains only first 1k lines.'
    st.markdown(href, unsafe_allow_html=True)
