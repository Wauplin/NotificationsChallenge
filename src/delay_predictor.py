import time
import math
import numpy as np
import pandas as pd
from pathlib import Path

from src.utils import second_in_day, timestamp_to_day, timestamp_to_day_of_week, DAYS_OF_WEEK, timestamp_to_period_of_day

from src.reviewer import Reviewer
from src.streamer import NotificationStreamer
from src.bundlers.cheater_bundler import CheaterNotificationBundler

from constants import STATISTICS_DIRPATH, AUGUST_TRAIN_FILEPATH


class DelayPredictor(object):
    """docstring for DelayPredictor."""

    def __init__(self, csvpath=AUGUST_TRAIN_FILEPATH):
        self.csvpath = Path(csvpath)
        self.statistics = None
        if not self._statistics_filepath().exists():
            self._train()
            self._save_statistics()
        else:
            self._load_statistics()

    def predict(self, timestamp, user_nb_sent_notifications_current_day):
        day_of_week = timestamp_to_day_of_week(timestamp)
        period_of_day = timestamp_to_period_of_day(timestamp)

        assert(user_nb_sent_notifications_current_day >= 0)
        if user_nb_sent_notifications_current_day > 3:
            user_nb_sent_notifications_current_day = 3

        try:
            return self.statistics.loc[day_of_week, period_of_day, user_nb_sent_notifications_current_day].delay
        except KeyError:
            pass

        return self.statistics.mean().delay

    def _statistics_filepath(self):
        return STATISTICS_DIRPATH / self.csvpath.name

    def _load_statistics(self):
        df = pd.read_csv(self._statistics_filepath())
        df['delay'] = df['delay'].apply(lambda x: pd.Timedelta(seconds=x))
        self.statistics = df.set_index([
            'day_of_week',
            'period_of_day',
            'user_nb_sent_notifications_today',
        ])

    def _save_statistics(self):
        df = self.statistics.copy()
        df['delay'] = df['delay'].apply(lambda x: x.total_seconds())
        df.reset_index().to_csv(
            self._statistics_filepath(),
            header=True,
            index=False,
        )

    def _train(self):
        streamer = NotificationStreamer(self.csvpath, limit=-1)
        bundler = CheaterNotificationBundler()
        reviewer = Reviewer()

        bundled_notifications = bundler.export(streamer.stream())
        notifications = streamer.notifications
        review = reviewer.review(notifications, bundled_notifications)

        notifications_dict = notifications.to_dict(orient='records')
        bundled_notifications_dict = bundled_notifications.to_dict(orient='records')

        # Count nb notifications today per user
        today_per_user = {}
        today_count_per_user = {}
        user_nb_sent_notifications_today_per_initial_notification = {}
        for bundled_notification in bundled_notifications_dict:
            user_id = bundled_notification['receiver_id']
            if today_per_user.get(user_id) != bundled_notification['notification_sent_day']:
                today_per_user[user_id] = bundled_notification['notification_sent_day']
                today_count_per_user[user_id] = -1
            today_count_per_user[user_id] += 1
            for notification_id in bundled_notification['base_notification_ids']:
                user_nb_sent_notifications_today_per_initial_notification[
                    notification_id] = today_count_per_user[user_id]

        notifications['user_nb_sent_notifications_today'] = notifications['notification_id'].map(
            user_nb_sent_notifications_today_per_initial_notification)

        notifications['day_of_week'] = notifications['timestamp'].apply(timestamp_to_day_of_week)
        notifications['period_of_day'] = notifications['timestamp'].apply(
            timestamp_to_period_of_day)

        self.statistics = notifications.groupby([
            'day_of_week',
            'period_of_day',
            'user_nb_sent_notifications_today'
        ]).agg(delay=pd.NamedAgg('delay', lambda x: x.quantile(0.80)))

    def get_user_criticity(average_nb_of_notifications_per_day):
        if average_nb_of_notifications_per_day == 0:  # First time we see the user
            return 'normal'
        elif average_nb_of_notifications_per_day in range(1, 3):
            return 'quiet'
        elif average_nb_of_notifications_per_day in range(3, 5):
            return 'normal'
        elif average_nb_of_notifications_per_day in range(5, 10):
            return 'spammed'
        elif average_nb_of_notifications_per_day > 10:
            return 'over-spammed'
