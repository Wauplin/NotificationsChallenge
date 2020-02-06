"""
python cli.py --input-file='datasets/notifications.csv' --output-file='output.csv'

usage: cli.py [-h] [-i INPUT_FILE] [-o OUTPUT_FILE] [--stdout]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        Path to raw notifications filepath.
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Path to output filepath. File will be overwritten if
                        exists.
  --stdout              Print to stdout if True.
  
"""

import time

from src.exporter import Exporter
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
                    default=True,
                    action='store_true',
                    help='Print to stdout if True.')
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

t1 = time.time()
print(f'Done. Took {round(t1-t0, 1)}s.')
