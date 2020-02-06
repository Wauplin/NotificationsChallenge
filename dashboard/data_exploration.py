import math
import time
import code
import random
import numpy as np
import pandas as pd
import streamlit as st
from collections import defaultdict

import plotly.express as px
import plotly.graph_objects as go

from constants import DATASETS_DIRPATH
from dashboard.st_utils.write_df import write_df
from src.utils import DAYS_OF_WEEK, timestamp_to_day_of_week

HOURS = list(range(2, 26, 2))
csv_path = DATASETS_DIRPATH / 'notifications.csv'


@st.cache
def read_csv(csv_path):
    cols = ['timestamp', 'user_id', 'friend_id', 'friend_name']
    notifications = pd.read_csv(csv_path, header=None)
    notifications.columns = cols
    notifications['timestamp'] = notifications['timestamp'].astype('datetime64[ns]')
    notifications.sort_values('timestamp', inplace=True)
    notifications['day_of_week'] = notifications['timestamp'].apply(timestamp_to_day_of_week)
    notifications['day_of_week'] = pd.Categorical(notifications['day_of_week'], DAYS_OF_WEEK)
    notifications['day'] = notifications['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d'))
    notifications['second_in_day'] = notifications['timestamp'].apply(
        lambda x: x.hour * 3600 + x.minute * 60 + x.second)
    for hour in HOURS:
        notifications[f'is_before_{hour}'] = notifications['second_in_day'] < hour * 3600
    return notifications


@st.cache
def compute_stats(notifications):
    stats = notifications.groupby('user_id').agg(
        nb_days_with_notifications=pd.NamedAgg('day', 'nunique'),
        max_notifications_in_a_day=pd.NamedAgg('day', lambda s: s.value_counts().max()),
    )
    stats = stats.reset_index().groupby(['nb_days_with_notifications', 'max_notifications_in_a_day']).agg(
        nb_users=pd.NamedAgg('user_id', 'nunique'),
    ).reset_index()
    stats['critical'] = (stats['max_notifications_in_a_day'] > 4).astype(int)
    stats['log_nb_users'] = stats['nb_users'].apply(lambda x: math.log10(x))
    return stats


@st.cache
def get_user_notifications(notifications, user_id):
    user_notifications = notifications[notifications['user_id'] == user_id].copy()
    critical_days = (user_notifications.groupby('day').agg(
        count=pd.NamedAgg('timestamp', 'count')) > 4)['count']
    user_notifications['critical'] = user_notifications['day'].map(
        lambda x: critical_days.get(x)).astype('int')
    return user_notifications


@st.cache
def histograms(notifications):
    count_per_user_per_day = notifications.groupby(['user_id', 'day']).count()[
        'timestamp'].reset_index()
    count_per_user_per_day.columns = ['user_id', 'day', 'count']
    over_notified_users = count_per_user_per_day[count_per_user_per_day['count'] > 4]

    mean_nb_per_user = count_per_user_per_day.groupby('user_id').agg(
        count=pd.NamedAgg('count', 'mean')
    )

    median_nb_per_user = count_per_user_per_day.groupby('user_id').agg(
        count=pd.NamedAgg('count', 'median')
    )

    percentile90_nb_per_user = count_per_user_per_day.groupby('user_id').agg(
        count=pd.NamedAgg('count', lambda x: x.quantile(0.90))
    )

    bins = [1, 2, 3, 4, 8, 10, mean_nb_per_user.values.max()]
    bins_str = [f'{int(x0)}-{int(x1)}' for x0, x1 in zip(bins[:-1], bins[1:])]
    hist_mean = np.histogram(mean_nb_per_user.values, bins)[0]
    hist_median = np.histogram(median_nb_per_user.values, bins)[0]
    hist_90 = np.histogram(percentile90_nb_per_user.values, bins)[0]
    fig = go.Figure([
        go.Bar(x=bins_str, y=hist_mean, name='Average number'),
        go.Bar(x=bins_str, y=hist_median, name='Median number'),
        go.Bar(x=bins_str, y=hist_90, name='90% percentile number'),
    ])
    return count_per_user_per_day, over_notified_users, fig


def data_exploration():
    st.title('Data exploration')

    st.write('''
    In this page, I develop the diggings I did before starting to implement a solution.

    I have a strong belief that this exploration part could go a lot further with more time allocated to it.

    In particular, I did not explore friends interactions.
    ''')

    ########################################################################
    notifications = read_csv(csv_path)
    write_df('Inital dataset', notifications)

    ########################################################################
    nb_notifications = len(notifications)
    nb_users = len(notifications['user_id'].unique())
    nb_friend = len(notifications['friend_id'].unique())
    nb_users_days = len(notifications[['user_id', 'day']].drop_duplicates())
    duration = (notifications['timestamp'].max() - notifications['timestamp'].min()).days

    st.write('\n'.join([
        f'### Key numbers\n'
        f'- Sent **{nb_notifications} notifications**',
        f'- to **{nb_users} users**',
        f'- from **{nb_friend} friends**',
        f'- over **{duration} days**',
        # f'- {nb_users_days} user-day pairs',
    ]))

    st.write('''
    ### Dataset splitting


    First thing I did with this dataset was to split it into a training and a test dataset.
    The idea is see if the hypothesis I was doing on one part of the data were still true on the other one.


    In our case, a random sampling of the notifications is not efficient since they can be very correlated.
    What I did is :
    - split the users (receivers) in two groups
    - temporally split the notifications in half


    This gave me 4 datasets :
    - a training dataset, only on data from August
    - a testing dataset only on data from August, in order to measure performance on a different subset of users.
    - a testing dataset only on data from September but with training users, in order to measure the difference between the month of August and the month of September.
    - a testest dataset with test users and September data, in order to combine both benefits.


    To be honest, even if I splitted the dataset in those 4 parts, I did not have the time to really study the differences between them. Also, I realized that a better split was possible by distinguishing groups of friend. In my splitting, a friend could have sent a notification at the same time to two different users, one in the train set and one in the test set.

    ''')

    st.info(f'Data loaded from {csv_path}')

    ########################################################################

    st.write('### Histogram of average nb of notification per day per user')

    count_per_user_per_day, over_notified_users, fig = histograms(notifications)
    st.write(fig)
    st.write('''
    Figure that shows the average number of notifications per day per user.

    What we can get out of this figure the fact that most users are below the threshold (4 notifications per day) in most of the cases.

    However, a non-negligeable part of the users are regularly spammed.
    ''')

    write_df('Over notififed users', over_notified_users)
    st.write(f'**Cumulated number of days with a user over notified :** {len(over_notified_users)}')

    ########################################################################

    stats = compute_stats(notifications)

    st.write('### Repartition of users')

    st.write('''
    Below figure show a repartition of the users based on the notifications they receive. Each point represent a group of users. The larger is the dot, the more users there is.

    In abscissa, the number of different days the user received a notification.

    In ordinate, the maximum number of notifications the user received in a single day.

    In a way, all users below the threshold (red line) don't need any help from our bundler. A good predictor of whether the user belongs to this category or not would be a really good way to assure a minimal delay to most of our users. This option is briefly discussed in the DelayPredictor section.
    ''')

    fig = px.scatter(
        stats,
        x='nb_days_with_notifications',
        y='max_notifications_in_a_day',
        size='log_nb_users',
        color='critical',
        hover_data=['nb_users'],
    )
    fig.add_shape(
        go.layout.Shape(
            type="line",
            x0=0, y0=4.5, x1=max(stats['nb_days_with_notifications']), y1=4.5,
            line={'color': 'red', 'width': 3}
        ))
    fig.update_layout(yaxis_type="log")
    st.write(fig)

    ########################################################################

    st.write('### Per-user exploration')

    st.write('''
    Often in datascience projects, it is a good idea to look precisely to the data line by line.

    In the figure below, we can explore the notifications for each users one by one. Each point is a notification. A notification is labelled as 'critical' when at least 4 notifications have been sent the same day for that user.

    In abscissa, the timestamp of the notification in second of the day.

    In ordinate, the day the notification has been received.
    ''')

    user_ids = notifications['user_id'].unique().tolist()
    user_id = st.selectbox('User id', user_ids[:100])
    user_notifications = get_user_notifications(notifications, user_id)
    fig = px.scatter(
        user_notifications,
        x='second_in_day',
        y='day',
        color='critical',
        hover_data=['second_in_day'],
    )
    st.write(fig)

    ########################################################################

    st.write('## By-day repartition')

    st.write('''
    Last intuition I wanted to confirm was the fact the number of notifications per day varies a lot depending on the day.

    First some days might be more sunny than others (so more people go for a tour). Second, some days of the week are more appropriate for a little hike.

    I also wanted to explore how early in the day we could predict that the day would be a good day. On the figures we can see that around 10-12am, we already have a pretty good idea of what will be the total number of notifications that day. However, I did not had the time to implement a proper algorithm to take advantage of it.
    ''')

    for groupby_key in ['day', 'day_of_week']:
        st.write(f'### Count notifications grouped by {groupby_key}')
        kwargs = {
            'count': pd.NamedAgg('timestamp', 'count'),
            # 'day_of_week': pd.NamedAgg('day_of_week', lambda x: x.iloc[0]),
        }
        for hour in HOURS:
            kwargs[f'count_before_{hour}'] = pd.NamedAgg(f'is_before_{hour}', 'sum')
        counts_per_day = notifications.groupby(groupby_key).agg(**kwargs).reset_index()

        # write_df('counts_per_day', counts_per_day)

        fig = go.Figure()
        for hour in HOURS:
            hour_key = f'count_before_{hour}'
            fig.add_trace(
                go.Scatter(
                    x=counts_per_day[groupby_key],
                    y=counts_per_day[hour_key],
                    mode='lines',
                    name=hour_key,
                )
            )
        st.write(fig)

    ########################################################################
