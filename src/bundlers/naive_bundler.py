import random
import pandas as pd

from src.bundlers.base_bundler import BaseNotificationBundler


class NaiveNotificationBundler(BaseNotificationBundler):

    def bundle(self, stream):
        for notification in stream:
            bundled_notification = {
                'notification_sent': notification['timestamp'],
                'timestamp_first_tour': notification['timestamp'],
                'tours': 1,
                'receiver_id': notification['user_id'],
                'message': self.notifications_to_message([notification]),
                'base_notification_ids': [notification['notification_id']],
            }
            self.check_notification(bundled_notification)
            yield bundled_notification
