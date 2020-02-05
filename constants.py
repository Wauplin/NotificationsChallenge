from pathlib import Path

DATASETS_DIRPATH = Path('datasets')
STATISTICS_DIRPATH = Path('statistics')

DATASETS_DIRPATH.mkdir(exist_ok=True, parents=True)
STATISTICS_DIRPATH.mkdir(exist_ok=True, parents=True)

AUGUST_TRAIN_FILEPATH = DATASETS_DIRPATH / 'august_train_dataset.csv'

DF_STREAMLIT_LIMIT = 1000
