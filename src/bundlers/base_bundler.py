import pandas as pd


class BaseNotificationBundler(object):

    BUNDLED_NOTIFICATION_KEYS = set([
        'notification_sent',
        'timestamp_first_tour',
        'tours',
        'receiver_id',
        'message',
        'base_notification_ids',
    ])

    def __init__(self):
        pass

    def export(self, stream):
        bundled_notifications = [
            notification
            for notification
            in self.bundle(stream)
        ]
        for notification in bundled_notifications:
            self.check_notification(notification)
        df = pd.DataFrame(bundled_notifications)
        df = df.sort_values('notification_sent')
        return df

    def bundle(self, stream):
        raise NotImplementedError()

    def notifications_to_message(self, notifications):
        nb_notifications = len(notifications)
        assert(nb_notifications > 0)
        friend_name = notifications[0]['friend_name']
        if len(notifications) == 1:
            return f'{friend_name} went on a tour.'
        elif len(notifications) == 2:
            return f'{friend_name} and 1 other went on a tour.'
        else:
            return f'{friend_name} and {nb_notifications-1} others went on a tour.'

    @classmethod
    def check_notification(cls, notification):
        assert(cls.BUNDLED_NOTIFICATION_KEYS == set(notification.keys()))
