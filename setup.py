import os
import random
import pandas as pd
from constants import DATASETS_DIRPATH


def select_august(df):
    return df[df[0] < '2017-09-01']


def select_september(df):
    return df[df[0] >= '2017-09-01']


def split_train_test(df):
    users = list(df[1].unique())
    nb_users = len(users)
    train_users = random.sample(users, int(0.6 * nb_users))
    test_users = list(set(users) - set(train_users))
    train_df = df[df[1].isin(train_users)]
    test_df = df[df[1].isin(test_users)]
    return train_df, test_df


def to_csv(df, path):
    df.to_csv(path, index=False, header=False)


if len(list(DATASETS_DIRPATH.glob('*.csv'))) == 0:
    url = os.environ.get('CHALLENGE_CSV')
    dataset = pd.read_csv(url, header=None)
    train_dataset, test_dataset = split_train_test(dataset)
    to_csv(dataset, DATASETS_DIRPATH / 'notifications.csv')
    to_csv(select_august(train_dataset), DATASETS_DIRPATH / 'august_train_dataset.csv')
    to_csv(select_september(train_dataset), DATASETS_DIRPATH / 'september_train_dataset.csv')
    to_csv(select_august(test_dataset), DATASETS_DIRPATH / 'august_test_dataset.csv')
    to_csv(select_september(test_dataset), DATASETS_DIRPATH / 'september_test_dataset.csv')
