import time
from pprint import pprint

from src.exporter import Exporter
from src.reviewer import Reviewer
from src.streamer import NotificationStreamer
from src.bundlers.statistical_waiter_bundler import StatisticalWaiterNotificationBundler

from constants import DATASETS_DIRPATH

import argparse
parser = argparse.ArgumentParser()


parser.add_argument('-i',
                    '--input-file',
                    type=str,
                    help='Path to raw notifications filepath.')
parser.add_argument('-o',
                    '--output-file',
                    type=str,
                    default='output.csv',
                    help='Path to output filepath. File will be overwritten if exists.')
parser.add_argument('--stdout',
                    default=False,
                    action='store_true',
                    help='Print to stdout if True.')
parser.add_argument('--review',
                    default=False,
                    action='store_true',
                    help='Print review to stdout if True.')
args = parser.parse_args()

t0 = time.time()

print(f'Load notifications from {args.input_file}.')
streamer = NotificationStreamer(args.input_file)
print(f'{len(streamer.notifications)} notifications found.')

print('Load StatisticalWaiterNotificationBundler.')
bundler = StatisticalWaiterNotificationBundler(DATASETS_DIRPATH / 'notifications.csv')

print('Process bundler.')
bundled_notifications = bundler.export(streamer.stream())

print(f'Save bundled notifications to {args.output_file}.')
Exporter(bundled_notifications).save_to(args.output_file)

if args.stdout:
    print(Exporter(bundled_notifications).format())

if args.review:
    print('Process reviewer.')
    pprint(Reviewer().review(streamer.notifications, bundled_notifications))

t1 = time.time()
print(f'Done. Took {round(t1-t0, 1)}s.')
