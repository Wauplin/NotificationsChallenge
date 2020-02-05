import pandas as pd

from src.bundlers.base_bundler import BaseNotificationBundler


class WaiterNotificationBundler(BaseNotificationBundler):
    """
    docstring for WaiterNotificationBundler.
    """

    def __init__(self, default_waiting_time_in_hour=1):
        self.default_waiting_time = pd.Timedelta(hours=default_waiting_time_in_hour)
        self.waiting_notifications = {}
        self.sent_bundled_notifications = []

    def bundle(self, stream):
        for notification in stream:
            self._new_notification(notification)
            user_id = notification['user_id']
            user_notifications = self._get_user_current_batch(user_id)
            if user_notifications.get('next_batch_dtm') is None:
                self._start_new_batch(user_notifications, notification)
            elif notification['timestamp'] <= user_notifications['next_batch_dtm']:
                self._add_to_batch(user_notifications, notification)
            else:
                self._send_batch(user_notifications)
                self._start_new_batch(user_notifications, notification)

        self._send_remaining_batches()

        for bundled_notifications in self.sent_bundled_notifications:
            yield bundled_notifications

    def _get_user_current_batch(self, user_id):
        if user_id not in self.waiting_notifications:
            self.waiting_notifications[user_id] = {}
        return self.waiting_notifications[user_id]

    def _new_notification(self, notification):
        pass

    def _start_new_batch(self, user_notifications, notification):
        assert(user_notifications.get('next_batch_dtm') is None)
        user_notifications['next_batch_dtm'] = self._get_next_batch_dtm(notification)
        user_notifications['next_batch_notifications'] = [notification]

    def _add_to_batch(self, user_notifications, notification):
        assert(user_notifications.get('next_batch_dtm') is not None)
        user_notifications['next_batch_notifications'].append(notification)

    def _send_batch(self, user_notifications):
        notifications = user_notifications['next_batch_notifications']
        assert(len(notifications) > 0)
        self.sent_bundled_notifications.append({
            'notification_sent': user_notifications['next_batch_dtm'],
            'timestamp_first_tour': notifications[0]['timestamp'],
            'tours': len(notifications),
            'receiver_id': notifications[0]['user_id'],
            'message': self.notifications_to_message(notifications),
            'base_notification_ids': [notification['notification_id'] for notification in notifications],
        })
        user_notifications['next_batch_dtm'] = None
        user_notifications['next_batch_notifications'] = []

    def _send_remaining_batches(self):
        for user_id, user_notifications in self.waiting_notifications.items():
            if len(user_notifications.get('next_batch_notifications', [])) > 0:
                self._send_batch(user_notifications)

    def _get_next_batch_dtm(self, notification):
        return notification['timestamp'] + self.default_waiting_time
