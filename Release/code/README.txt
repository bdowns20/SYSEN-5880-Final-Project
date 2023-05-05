# README

## Script Description
The following explains what each script/Jupyter Notebook does.

nfl_player_download.py - This script downloads the player statisics for All Pro and Pro Bowl players in the years 2002 - 2020
nfl_weather.py - This script downloads historical weather data
nfl_team_download.py - This script downloads team specific statistics in the year 2002 - 2020
data_frame_merge.py - This script combines all the different datasets into a single CSV file
feature_drop.py - This script drops features that are not necessary for the notebooks

## Python Modules Used

The following modules are needed:
- Pandas
- ScikitLearn
- NumPy
- Seaborn
- B4 (BeautifulSoup)
- SportsReference API

## Instructions

Please note that all data has been downloaded and is included in the data directory except for the large Kaggle dataset (https://www.kaggle.com/maxhorowitz/nflplaybyplay2009to2016?select=NFL+Play+by+Play+2009-2018+%28v5%29.csv). This can be downloaded at the Kaggle site provided or from the Google Drive URL (Add URL)

To generate the full dataset file, you need to ensure the Kaggle file is in the data folder and renamed to nfl_play_by_play09-18.csv.

Run the data_frame_merge.py script: python3 data_frame_merge.py. This will take a few minutes due to the large size of data.

Next, you need to drop the features that are not needed by running the feature_drop.py script.

usage: feature_drop.py [-h] -f data [-s data]

Feature Dropper

optional arguments:
  -h, --help            show this help message and exit
  -f data, --file data  Full path to CSV to drop features from
  -s data, --save data  Full path and file name to save the data to

The complete dataset has now been generated. To run the models and visualizations, use the NFL Play Classification.ipynb Jupyter Notebook.
