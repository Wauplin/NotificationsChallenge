import pandas as pd

from src.delay_predictor import DelayPredictor
from src.bundlers.waiter_bundler import WaiterNotificationBundler

from src.utils import second_in_day, timestamp_to_day, timestamp_to_day_of_week


class StatisticalWaiterNotificationBundler(WaiterNotificationBundler):
    """docstring for StatisticalWaiterNotificationBundler."""

    def __init__(self, train_filepath=None):
        self.parent_class = super(StatisticalWaiterNotificationBundler, self)
        self.parent_class.__init__()

        self.current_day = None
        self.nb_notifications_current_day = None

        self.delay_predictor = DelayPredictor(train_filepath)

        self.user_current_day = {}
        self.user_nb_notifications_current_day = {}
        self.user_nb_sent_notifications_current_day = {}

    def _get_next_batch_dtm(self, notification):
        delay = self.delay_predictor.predict(
            timestamp=notification['timestamp'],
            user_nb_sent_notifications_current_day=self.user_nb_sent_notifications_current_day.get(
                notification['user_id'], 0),
        )
        return notification['timestamp'] + delay

    def _new_notification(self, notification):
        notification_day = timestamp_to_day(notification['timestamp'])
        if notification_day != self.current_day:
            self.current_day = notification_day
            self.nb_notifications_current_day = 0
        self.nb_notifications_current_day += 1

    def _send_batch(self, user_notifications):
        next_batch_notifications = user_notifications['next_batch_notifications']
        if len(next_batch_notifications) > 0:
            first_notification = next_batch_notifications[0]
            user_id = first_notification['user_id']
            notification_day = timestamp_to_day(first_notification['timestamp'])
            user_current_day = self.user_current_day.get(user_id)
            if notification_day != user_current_day:
                self.user_current_day[user_id] = notification_day
                self.user_nb_notifications_current_day[user_id] = 0
                self.user_nb_sent_notifications_current_day[user_id] = -1
            self.user_nb_notifications_current_day[user_id] += len(next_batch_notifications)
            self.user_nb_sent_notifications_current_day[user_id] += 1
        self.parent_class._send_batch(user_notifications)
