DAYS_OF_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def second_in_day(ts):
    return ts.hour * 3600 + ts.minute * 60 + ts.second


def timestamp_to_day(ts):
    return ts.strftime('%Y-%m-%d')


def timestamp_to_day_of_week(ts):
    return DAYS_OF_WEEK[ts.dayofweek]


def timestamp_to_period_of_day(ts):
    if ts.hour < 6:
        return 'night'
    if ts.hour < 12:
        return 'morning'
    if ts.hour < 18:
        return 'afternoon'
    else:
        return 'evening'
