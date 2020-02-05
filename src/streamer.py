import pandas as pd
from pathlib import Path

from src.utils import second_in_day, timestamp_to_day


class NotificationStreamer(object):
    """docstring for NotificationStreamer."""
    INITIAL_COLUMNS = ['timestamp', 'user_id', 'friend_id', 'friend_name']

    def __init__(self, data, limit=None):
        if isinstance(data, str) or isinstance(data, Path):
            self.notifications = self.load_csv(str(data))
        elif isinstance(data, pd.DataFrame):
            for col in self.INITIAL_COLUMNS:
                assert(col in data.columns)
            self.notifications = data
        if limit is not None and limit != -1:
            self.notifications = self.notifications.head(limit).copy()

    @classmethod
    def load_csv(cls, csv_path):
        notifications = pd.read_csv(csv_path, header=None)
        notifications.columns = cls.INITIAL_COLUMNS
        notifications['timestamp'] = notifications['timestamp'].astype('datetime64[ns]')
        notifications.sort_values('timestamp', inplace=True)
        notifications['notification_id'] = notifications.index
        notifications['day'] = notifications['timestamp'].apply(timestamp_to_day)
        notifications['second_in_day'] = notifications['timestamp'].apply(second_in_day)
        return notifications

    def stream(self):
        """
        ~10x faster than df.iterrows(). Counterpart : full dictionnary is loaded in memory.
        """
        for notification in self.notifications.to_dict(orient='records'):
            yield notification
