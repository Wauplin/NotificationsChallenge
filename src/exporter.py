
class Exporter(object):
    """docstring for Exporter."""

    INITIAL_NOTIFICATIONS_COLUMNS = [
        'timestamp',
        'user_id',
        'friend_id',
        'friend_name'
    ]

    BUNDLED_NOTIFICATIONS_COLUMNS = [
        'notification_sent',
        'timestamp_first_tour',
        'tours',
        'receiver_id',
        'message',
    ]

    def __init__(self, notifications):
        self.notifications = notifications

    def save_to(self, output_file):
        self.format().to_csv(output_file, header=True, index=False)

    def format(self):
        if self.are_initial():
            assert(not self.are_bundled())
            df = self.notifications[self.INITIAL_NOTIFICATIONS_COLUMNS]
            df = df.sort_values('timestamp')
        elif self.are_bundled():
            assert(not self.are_initial())
            df = self.notifications[self.BUNDLED_NOTIFICATIONS_COLUMNS]
            df = df.sort_values('notification_sent')
        else:
            message = f'Missing columns in notifications to be exported : {self.notifications.columns}'
            raise ValueError(message)
        return df.reset_index(drop=True)

    def are_initial(self):
        return all([
            col in self.notifications.columns
            for col in self.INITIAL_NOTIFICATIONS_COLUMNS
        ])

    def are_bundled(self):
        return all([
            col in self.notifications.columns
            for col in self.BUNDLED_NOTIFICATIONS_COLUMNS
        ])
