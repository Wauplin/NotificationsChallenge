import pandas as pd
import streamlit as st
from collections import defaultdict


class Reviewer(object):
    """
    Nb notifications not sent.
    Nb notifications sent more than once.
    Nb notifications sent before timestamp.
    Percentiles and average delay between tour and notification.
    Nb of notifications above 4 per day.
    Nb of users spammed (above 4 in a single day)
    Nb of notifications above 8 per day.
    Nb of users over-spammed (above 8 in a single day).
    Total nb of users.
    Total nb of base notifications.
    Total nb of bundled notifications.
    """

    def __init__(self):
        self.last_results = None

    def review(self, notifications, bundled_notifications):
        results = {}

        nb_sent = defaultdict(int)
        notification_sent = {}
        for bundled_notification in bundled_notifications.to_dict(orient='records'):
            for id in bundled_notification['base_notification_ids']:
                nb_sent[id] += 1
                notification_sent[id] = bundled_notification['notification_sent']
        notifications['nb_sent'] = notifications.notification_id.map(nb_sent)
        notifications['notification_sent'] = notifications.notification_id.map(notification_sent)
        notifications['delay'] = notifications['notification_sent'] - notifications['timestamp']

        results['nb_base_notifications'] = notifications.shape[0]
        results['nb_bundled_notifications'] = bundled_notifications.shape[0]
        results['bundled_rate'] = 100.0 * (results['nb_base_notifications'] -
                                           results['nb_bundled_notifications']) / results['nb_base_notifications']
        results['nb_users'] = bundled_notifications['receiver_id'].unique().size

        results['nb_notifications_not_sent'] = (notifications['nb_sent'] == 0).sum()
        results['nb_notifications_sent_more_than_once'] = (notifications['nb_sent'] > 1).sum()

        bundled_notifications['notification_sent_day'] = bundled_notifications['notification_sent'].apply(
            lambda x: x.strftime('%Y-%m-%d'))

        bundled_notifications_counts = bundled_notifications.groupby(['receiver_id', 'notification_sent_day']).agg(
            count=pd.NamedAgg('notification_sent', 'count')
        ).reset_index()

        results['nb_notifications_above_4_per_day'] = (
            bundled_notifications_counts[bundled_notifications_counts['count'] > 4]['count'] - 4).sum()
        results['nb_notifications_above_8_per_day'] = (
            bundled_notifications_counts[bundled_notifications_counts['count'] > 8]['count'] - 8).sum()
        results['nb_users_spammed_above_4_per_day'] = len(
            bundled_notifications_counts[bundled_notifications_counts['count'] > 4]['receiver_id'].unique())
        results['nb_users_spammed_above_8_per_day'] = len(
            bundled_notifications_counts[bundled_notifications_counts['count'] > 8]['receiver_id'].unique())

        results['users_spammed_above_4_per_day_rate'] = 100.0 * \
            results['nb_users_spammed_above_4_per_day'] / results['nb_users']
        results['users_spammed_above_8_per_day_rate'] = 100.0 * \
            results['nb_users_spammed_above_8_per_day'] / results['nb_users']

        results['nb_notifications_sent_too_soon'] = (
            notifications['delay'].apply(lambda x: x.total_seconds()) < 0.0).sum()
        results['average_delay'] = notifications['delay'].mean()
        results['25_percentile_delay'] = notifications['delay'].quantile(0.25)
        results['50_percentile_delay'] = notifications['delay'].quantile(0.50)
        results['75_percentile_delay'] = notifications['delay'].quantile(0.75)
        results['90_percentile_delay'] = notifications['delay'].quantile(0.90)
        results['99_percentile_delay'] = notifications['delay'].quantile(0.99)

        self.last_results = results

        return results

    def display_review(self):
        results = self.last_results

        st.title('Review')
        if results is None:
            st.error('No review ot display.')
        else:
            requirements_dict = {
                'nb_users': {
                    'text': 'Number of users receiving notifications',
                    'must_be': None,
                    'format_str': None,
                },
                'nb_base_notifications': {
                    'text': 'Initial number of notifications',
                    'must_be': None,
                    'format_str': None,
                },
                'nb_bundled_notifications': {
                    'text': 'Number of bundled notifications',
                    'must_be': None,
                    'format_str': None,
                },
                'bundled_rate': {
                    'text': 'Decrease percentage',
                    'must_be': 'higher is better -between 0 and 100-',
                    'format_str': lambda x: f'{round(x, 2)}%',
                    'significant': True,
                },
                'nb_notifications_not_sent': {
                    'text': 'Number of initial notifications not sent',
                    'must_be': 0,
                    'format_str': None,
                },
                'nb_notifications_sent_more_than_once': {
                    'text': 'Number of initial notifications sent more than once',
                    'must_be': 0,
                    'format_str': None,
                },
                'nb_notifications_sent_too_soon': {
                    'text': 'Number of initial notifications sent too soon',
                    'must_be': 0,
                    'format_str': None,
                    'format_str': None,
                },
                'nb_notifications_above_4_per_day': {
                    'text': 'Number of bundled notifications above 4 per day',
                    'must_be': 'lower is better',
                    'format_str': None,
                },
                'nb_notifications_above_8_per_day': {
                    'text': 'Number of bundled notifications above 8 per day',
                    'must_be': 'lower is better',
                    'format_str': None,
                },
                'nb_users_spammed_above_4_per_day': {
                    'text': 'Number of users spammed above 4 bundled notifications per day',
                    'must_be': 'lower is better',
                    'format_str': None,
                },
                'nb_users_spammed_above_8_per_day': {
                    'text': 'Number of users spammed above 8 bundled notifications per day',
                    'must_be': 'lower is better',
                    'format_str': None,
                },
                'users_spammed_above_4_per_day_rate': {
                    'text': 'Users spammed above 4 bundled notifications per day (rate)',
                    'must_be': 'lower is better',
                    'format_str': lambda x: f'{round(x, 2)}%',
                    'significant': True,
                },
                'users_spammed_above_8_per_day_rate': {
                    'text': 'Users spammed above 8 bundled notifications per day (rate)',
                    'must_be': 'lower is better',
                    'format_str': lambda x: f'{round(x, 2)}%',
                },
                'average_delay': {
                    'text': 'Average delay',
                    'must_be': 'lower is better',
                    'format_str': format_timedelta,
                    'significant': True,
                },
                '25_percentile_delay': {
                    'text': 'Delay percentile (25%)',
                    'must_be': 'lower is better',
                    'format_str': format_timedelta,
                },
                '50_percentile_delay': {
                    'text': 'Delay percentile (50%)',
                    'must_be': 'lower is better',
                    'format_str': format_timedelta,
                    'significant': True,
                },
                '75_percentile_delay': {
                    'text': 'Delay percentile (75%)',
                    'must_be': 'lower is better',
                    'format_str': format_timedelta,
                },
                '90_percentile_delay': {
                    'text': 'Delay percentile (90%)',
                    'must_be': 'lower is better',
                    'format_str': format_timedelta,
                },
                '99_percentile_delay': {
                    'text': 'Delay percentile (99%)',
                    'must_be': 'lower is better',
                    'format_str': format_timedelta,
                },
            }

            st.write('### Metrics :')
            for key, requirements in requirements_dict.items():
                if requirements.get('significant'):
                    if requirements['format_str'] is None:
                        result_str = results[key]
                    else:
                        result_str = requirements['format_str'](results[key])
                    sentence = f'{requirements["text"]} : {result_str}'
                    st.info(sentence)

            list_to_display = [
                'nb_users',
                'nb_base_notifications',
                'nb_bundled_notifications',
                'bundled_rate',
                'nb_notifications_not_sent',
                'nb_notifications_sent_more_than_once',
                'nb_notifications_sent_too_soon',
                'nb_notifications_above_4_per_day',
                'nb_notifications_above_8_per_day',
                'nb_users_spammed_above_4_per_day',
                'nb_users_spammed_above_8_per_day',
                'users_spammed_above_4_per_day_rate',
                'users_spammed_above_8_per_day_rate',
            ]

            st.write('### Key numbers :')
            for key in list_to_display:
                self.display_line(results[key], requirements_dict[key])

            list_to_display = [
                'average_delay',
                '25_percentile_delay',
                '50_percentile_delay',
                '75_percentile_delay',
                '90_percentile_delay',
                '99_percentile_delay',
            ]

            st.write('### Delay repartition :')
            for key in list_to_display:
                self.display_line(results[key], requirements_dict[key])

    @staticmethod
    def display_line(result, requirements):
        if requirements['format_str'] is None:
            result_str = result
        else:
            result_str = requirements['format_str'](result)

        sentence = f'{requirements["text"]} : {result_str}'
        if requirements.get('significant'):
            sentence = f'**{sentence}**'

        if requirements['must_be'] is None:
            st.write(sentence)
        elif isinstance(requirements['must_be'], str):
            st.write(f'{sentence} ({requirements["must_be"]})')
        else:
            assert(isinstance(requirements['must_be'], int))
            if requirements['must_be'] != result:
                st.warning(f'{sentence} ({requirements["must_be"]})')


def format_timedelta(td):
    total_seconds = td.total_seconds()
    hour = int(total_seconds / 3600)
    minute = int((total_seconds % 3600) / 60)
    second = int(total_seconds % 60)
    return f'{hour}h {minute}m {second}s'
