import time
import streamlit as st

from src.reviewer import Reviewer
from src.exporter import Exporter
from src.streamer import NotificationStreamer

from src.bundlers.naive_bundler import NaiveNotificationBundler
from src.bundlers.waiter_bundler import WaiterNotificationBundler
from src.bundlers.statistical_waiter_bundler import StatisticalWaiterNotificationBundler
from src.bundlers.cheater_bundler import CheaterNotificationBundler

from constants import DATASETS_DIRPATH, DF_STREAMLIT_LIMIT

DATASETS_PATHS = list(DATASETS_DIRPATH.glob('*.csv'))


def write_df(title, df):
    st.write(f'### {title}')
    data = df.head(DF_STREAMLIT_LIMIT).copy()
    for col in data.columns:
        if str(data[col] == 'category'):
            data[col] = data[col].astype('str')
    st.write(data)


path = st.sidebar.selectbox('Dataset file', DATASETS_PATHS)

limit = st.sidebar.number_input(
    'Number of notifications to load',
    min_value=-1,
    max_value=None,
    value=10000,
    step=10000,
)


bundler_class = st.sidebar.selectbox('Bundler', options=[
    WaiterNotificationBundler,
    NaiveNotificationBundler,
    CheaterNotificationBundler,
    StatisticalWaiterNotificationBundler,
], format_func=lambda x: x.__name__)

if bundler_class is WaiterNotificationBundler:
    default_waiting_time_in_hour = st.sidebar.number_input(
        'Default waiting time (in hour)',
        min_value=0.,
        max_value=24.,
        value=1.,
        step=0.25,
    )
    bundler_kwargs = {'default_waiting_time_in_hour': default_waiting_time_in_hour}
else:
    bundler_kwargs = {}


streamer = NotificationStreamer(path, limit=limit)
bundler = bundler_class(**bundler_kwargs)
reviewer = Reviewer()

st.title(f'Bundler : {bundler.__class__.__name__}')
st.write(bundler.__doc__)

st.title('Processing')

with st.spinner('Processing bundler...'):
    t0 = time.time()
    bundled_notifications = bundler.export(streamer.stream())
    t1 = time.time()
    st.success(f'Bundler finished in {round(t1-t0, 2)}s')

with st.spinner('Processing reviewer...'):
    t0 = time.time()
    review = reviewer.review(streamer.notifications, bundled_notifications)
    t1 = time.time()
    st.success(f'Reviewer finished in {round(t1-t0, 2)}s')

reviewer.display_review()

st.title('Exports')
write_df('Initial notifications', Exporter(streamer.notifications).format())
write_df('Bundled notifications', Exporter(bundled_notifications).format())
