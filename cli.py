"""
python cli.py --input-file='datasets/notifications.csv' --output-file='output.csv'
"""

import time

from src.exporter import Exporter
from src.streamer import NotificationStreamer
from src.bundlers.statistical_waiter_bundler import StatisticalWaiterNotificationBundler

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
args = parser.parse_args()

t0 = time.time()

print(f'Load notifications from {args.input_file}.')
streamer = NotificationStreamer(args.input_file)
print(f'{len(streamer.notifications)} notifications found.')

print('Load StatisticalWaiterNotificationBundler.')
bundler = StatisticalWaiterNotificationBundler()

print('Process bundler.')
bundled_notifications = bundler.export(streamer.stream())

print(f'Save bundled notifications to {args.output_file}.')
Exporter(bundled_notifications).save_to(args.output_file)

t1 = time.time()
print(f'Done. Took {round(t1-t0, 1)}s.')
