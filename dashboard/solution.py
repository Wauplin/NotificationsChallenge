import time
import streamlit as st

from src.reviewer import Reviewer
from src.exporter import Exporter
from src.streamer import NotificationStreamer
from src.bundlers.statistical_waiter_bundler import StatisticalWaiterNotificationBundler

from dashboard.st_utils.write_df import write_df
from dashboard.st_utils.file_download import file_download

from constants import DATASETS_DIRPATH


def solution():
    st.title(f'Solution tool')

    st.write('''
    Page to upload and process an unseen dataset.


    Processing is done by the **StatisticalWaiterBundler** trained on all the initial dataset from challenge (`notifications.csv`).


    Results can be exported but are limited to first 5k rows due to technical issues. Processing is still done on all notifications.


    A performance review is also available at the bottom.
    ''')

    st.info('Delay predictor is trained on notifications.csv (full dataset).')

    st.markdown('**Upload dataset from url**')
    url_path = st.text_input('Dataset URL')

    if url_path is not None and url_path != '':

        st.title('CLI')
        st.write('Compute offline using the CLI interface :')
        st.write(f"```\npython cli.py --input-file='{url_path}' --output-file='output.csv' --review\n```")

        with st.spinner(f'Load data from {url_path}'):
            t0 = time.time()
            streamer = NotificationStreamer(url_path)
            t1 = time.time()
            st.success(f'Load data finished in {round(t1-t0, 2)}s')

        with st.spinner('Processing bundler...'):
            t0 = time.time()
            bundler = StatisticalWaiterNotificationBundler(DATASETS_DIRPATH / 'notifications.csv')
            bundled_notifications = bundler.export(streamer.stream())
            t1 = time.time()
            st.success(f'Bundler finished in {round(t1-t0, 2)}s')

        with st.spinner('Processing reviewer...'):
            t0 = time.time()
            reviewer = Reviewer()
            review = reviewer.review(streamer.notifications, bundled_notifications)
            t1 = time.time()
            st.success(f'Reviewer finished in {round(t1-t0, 2)}s')

        st.title('Exports')
        initial_notifications = Exporter(streamer.notifications).format()
        write_df('Initial notifications', initial_notifications)
        file_download(initial_notifications, 'initial_notifications')

        bundled_notifications = Exporter(bundled_notifications).format()
        write_df('Bundled notifications', bundled_notifications)
        file_download(bundled_notifications, 'bundled_notifications')

        st.title('Performances')
        reviewer.display_review()
