import time
import random
import numpy as np
import pandas as pd
from uuid import uuid4

from sklearn.cluster import KMeans

from src.bundlers.base_bundler import BaseNotificationBundler


class CheaterNotificationBundler(BaseNotificationBundler):
    """docstring for CheaterNotificationBundler."""

    def __init__(self):
        self.notifications = None
        self.bundles = None
        self.bundled_notifications = []

    def bundle(self, stream):
        self.notifications = pd.DataFrame([notification for notification in stream])
        self.notifications.groupby(['user_id', 'day']).apply(lambda df: self.perfect_matcher(df))
        for notification in self.bundled_notifications:
            yield notification

    def perfect_matcher(self, df):
        if len(df) > 4:
            X = df['second_in_day'].values.reshape((-1, 1))
            km = KMeans(n_clusters=4)
            y = km.fit_predict(X)
            for i in range(4):
                notifications = df[y == i]
                self.bundled_notifications.append({
                    'notification_sent': notifications['timestamp'].max(),
                    'timestamp_first_tour': notifications['timestamp'].min(),
                    'tours': len(notifications),
                    'receiver_id': notifications['user_id'].iloc[0],
                    'message': self.notifications_to_message(notifications.to_dict(orient='records')),
                    'base_notification_ids': list(notifications['notification_id']),
                })
        else:
            for irow, row in df.iterrows():
                self.bundled_notifications.append({
                    'notification_sent': row['timestamp'],
                    'timestamp_first_tour': row['timestamp'],
                    'tours': 1,
                    'receiver_id': row['user_id'],
                    'message': self.notifications_to_message([dict(row)]),
                    'base_notification_ids': [row['notification_id']],
                })
