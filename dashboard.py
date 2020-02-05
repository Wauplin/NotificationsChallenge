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

from src.utils import DAYS_OF_WEEK, timestamp_to_day_of_week

DF_STREAMLIT_LIMIT = 1000
DAYS_OF_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
HOURS = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]

csv_path = 'august_train_dataset.csv'
st.info(f'Data loaded from {csv_path}')


def write_df(title, df):
    st.write(f'### {title}')
    data = df.head(DF_STREAMLIT_LIMIT).copy()
    for col in data.columns:
        if str(data[col] == 'category'):
            data[col] = data[col].astype('str')
    st.write(data)


st.write('# Komoot Dashboard')

########################################################################
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


notifications = read_csv(csv_path)
write_df('Notifications', notifications)

########################################################################
nb_users = len(notifications['user_id'].unique())
nb_friend = len(notifications['friend_id'].unique())
nb_users_days = len(notifications[['user_id', 'day']].drop_duplicates())
st.write(f'{nb_users} users, {nb_friend} friends, {nb_users_days} user-day pairs')


########################################################################
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

bins = [1, 2, 3, 4, 8, 10, mean_nb_per_user.values.max()]
bins_str = [f'{int(x0)}-{int(x1)}' for x0, x1 in zip(bins[:-1], bins[1:])]
hist_mean = np.histogram(mean_nb_per_user.values, bins)[0]
hist_median = np.histogram(median_nb_per_user.values, bins)[0]
fig = go.Figure([
    go.Bar(x=bins_str, y=hist_mean),
    go.Bar(x=bins_str, y=hist_median),
])

st.write('### Histogram of average nb of notification per day per user')
st.write(fig)

write_df('Over notififed users', over_notified_users)
st.write(f'Nb over notified users {len(over_notified_users)}')

########################################################################
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


stats = compute_stats(notifications)

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


@st.cache
def get_user_notifications(user_id):
    user_notifications = notifications[notifications['user_id'] == user_id].copy()
    critical_days = (user_notifications.groupby('day').agg(
        count=pd.NamedAgg('timestamp', 'count')) > 4)['count']
    user_notifications['critical'] = user_notifications['day'].map(
        lambda x: critical_days.get(x)).astype('int')
    return user_notifications


user_ids = notifications['user_id'].unique().tolist()
user_id = st.selectbox('User id', user_ids[:100])
user_notifications = get_user_notifications(user_id)
fig = px.scatter(
    user_notifications,
    x='second_in_day',
    y='day',
    color='critical',
    hover_data=['second_in_day'],
)
st.write(fig)

########################################################################


for groupby_key in ['day', 'day_of_week']:
    st.write(f'### Count notifications grouped by {groupby_key}')
    kwargs = {
        'count': pd.NamedAgg('timestamp', 'count'),
        # 'day_of_week': pd.NamedAgg('day_of_week', lambda x: x.iloc[0]),
    }
    for hour in HOURS:
        kwargs[f'count_before_{hour}'] = pd.NamedAgg(f'is_before_{hour}', 'sum')
    counts_per_day = notifications.groupby(groupby_key).agg(**kwargs).reset_index()

    write_df('counts_per_day', counts_per_day)

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
