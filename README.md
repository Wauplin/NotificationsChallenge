# Application Challenge - Caunil

## Purpose

This repository contains the code, documentation and report for a job application. The Challenge needed to be completed within a week.

## Disclaimer

The company name is never mentioned in the code or in the documentation. An environment variable is used to make it appear on the dashboard but it is a purely cosmetic addition.

## Repository architecture

```
- dashboard/                        <- contains all scripts to display the dashboard
- datasets/                         <- downloaded at setup
- doc/                              <- documentation (displayed in dashboard)
    - components_presentation.md    
    - summary.md
    - conclusion.md                 <- what did I learn from this project
- src/                              <- key resources for the algorithm
- statistics/                       <- also downloaded at setup
- app.py                            <- launch dashboard
- cli.py                            <- Command Line Interface script
- constants.py                      <- some constants for the project
- Pipfile
- Pipfile.lock
- Procfile                          <- Heroku deploy
- setup.py              
- setup.sh
```

## Getting started

### Environment variables

Some environment variables are needed for the module to be operational. Please add a `.env` file at the root of the repository containing following keys. An example of file should have been sent to you. The `.env` file will be automatically loaded by Pipenv.

```
CHALLENGE_LOGIN=
CHALLENGE_PASSWORD=
CHALLENGE_LOGO=
CHALLENGE_CSV=
CHALLENGE_NOTIFICATIONS_STATISTICS=
CHALLENGE_TRAIN_AUGUST_STATISTICS=
```

### Install

In order to install the dependencies and run the project, Pipenv is required. [Pipenv is a popular Python Packaging Tool](https://pipenv.kennethreitz.org/en/latest/). Use it as follow :
```
pipenv install    # install dependencies
pipenv shell      # enter shell
```

Then, project setup needs to be done. It will download some data and statistics files. /!\\ `.env` file must have been filled.   
Run (within Pipenv shell):
```
sh setup.sh
python setup.py
```

Project is now correctly installed !

### Command Line Interface

A CLI is available to process any notifications dataset.

#### Example of use :
```
python cli.py --input-file='datasets/notifications.csv' --output-file='output.csv' --review
```

#### Usage :
```
usage: cli.py [-h] [-i INPUT_FILE] [-o OUTPUT_FILE] [--stdout] [--review]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        Path to raw notifications filepath.
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Path to output filepath. File will be overwritten if
                        exists.
  --stdout              Print to stdout if True.
  --review              Print review to stdout if True.

```

### Streamlit dashboard

A dashboard is available to visualize results and test new datasets. I used [Streamlit](streamlit.io) to build it.
Dashboard requires a login/password to access it. Credentials can be found in the `.env` file.

#### Local execution

```
streamlit run app.py
```

#### Heroku app

A deployed version of the dashboard is also available on Heroku. The url to this dashboard must have been sent to you.
