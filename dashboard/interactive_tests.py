import time
import streamlit as st

from src.reviewer import Reviewer
from src.exporter import Exporter
from src.streamer import NotificationStreamer

from src.bundlers.naive_bundler import NaiveNotificationBundler
from src.bundlers.waiter_bundler import WaiterNotificationBundler
from src.bundlers.statistical_waiter_bundler import StatisticalWaiterNotificationBundler
from src.bundlers.cheater_bundler import CheaterNotificationBundler

from constants import DATASETS_DIRPATH
from dashboard.st_utils.write_df import write_df
from dashboard.st_utils.file_download import file_download


DATASETS_PATHS = list(DATASETS_DIRPATH.glob('*.csv'))


def interactive_tests():

    st.sidebar.markdown('**Choose local csv...**')
    path = st.sidebar.selectbox('Dataset file', DATASETS_PATHS)

    st.sidebar.markdown('**...or upload from url**')
    url_path = st.sidebar.text_input('Dataset URL')
    if url_path is not None and url_path != '':
        st.warning('Tests from URL are not efficient since the file is downloaded multiple times.')
        path = url_path

    st.sidebar.markdown('**Parameters of the test**')

    limit = st.sidebar.number_input(
        'Number of notifications to load (-1 to load all dataset)',
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

    st.title(f'{bundler.__class__.__name__}')
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
    initial_notifications = Exporter(streamer.notifications).format()
    write_df('Initial notifications', initial_notifications)
    file_download(initial_notifications, 'initial_notifications')

    bundled_notifications = Exporter(bundled_notifications).format()
    write_df('Bundled notifications', bundled_notifications)
    file_download(bundled_notifications, 'bundled_notifications')
