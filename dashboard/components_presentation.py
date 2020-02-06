import streamlit as st

from src.reviewer import Reviewer
from src.exporter import Exporter
from src.streamer import NotificationStreamer

from src.bundlers.base_bundler import BaseNotificationBundler
from src.bundlers.naive_bundler import NaiveNotificationBundler
from src.bundlers.waiter_bundler import WaiterNotificationBundler
from src.bundlers.statistical_waiter_bundler import StatisticalWaiterNotificationBundler
from src.bundlers.cheater_bundler import CheaterNotificationBundler


def components_presentation():
    components = {}
    components['Reviewer'] = Reviewer
    components['Exporter'] = Exporter
    components['NotificationStreamer'] = NotificationStreamer
    components['BaseNotificationBundler'] = BaseNotificationBundler
    components['NaiveNotificationBundler'] = NaiveNotificationBundler
    components['WaiterNotificationBundler'] = WaiterNotificationBundler
    components['StatisticalWaiterNotificationBundler'] = StatisticalWaiterNotificationBundler
    components['CheaterNotificationBundler'] = CheaterNotificationBundler

    component = components[st.sidebar.selectbox('Component', list(components.keys()))]

    st.title(f'{component.__name__}')
    st.write(component.__doc__)
