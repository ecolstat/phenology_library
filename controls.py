# Controls for web app dropdowns
import pathlib
import pandas as pd
from datetime import datetime
import os

# Get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath('data').resolve()

# Load datasets: Converted in external script from goeJSON to csv with x,y columns
df = pd.read_csv(DATA_PATH.joinpath('lcDF.csv'), index_col=0, parse_dates=['variable'])
df.columns = ['PointID', 'LC_code', 'reference_date', 'ndvi', 'lon', 'lat']

# NLCD codes for 2011 model
NLCD_2011 = {
    '11': 'Open Water',
    '12': 'Perennial Ice/Snow',
    '21': 'Developed, Open Space',
    '22': 'Developed, Low Intensity',
    '23': 'Developed, Medium Intensity',
    '24': 'Developed, High Intensity',
    '31': 'Barren Land (Rock/Sand/Clay)',
    '41': 'Deciduous Forest',
    '42': 'Evergreen Forest',
    '43': 'Mixed Forest',
    '51': 'Dwarf Scrub (AK only)',
    '52': 'Scrub/Scrub',
    '71': 'Grassland/Herbaceous',
    '72': 'Sedge/Herbaceous (AK only)',
    '73': 'Lichens (AK ony)',
    '74': 'Moss (AK only)',
    '81': 'Pasture/Hay',
    '82': 'Cultivated Crops',
    '90': 'Woody Wetlands',
    '95': 'Emergent Herbaceous Wetlands',
}

# TODO: this is hardcoded for specific input date format. Needs to generalize.
unique_dates = [str(x)[:10] for x in df.reference_date.unique()]

dates_list = [datetime.strptime(x, '%Y-%m-%d') for x in unique_dates]

# Note: this starts with DOY = 1.
DOYLIST = [x.timetuple().tm_yday for x in dates_list]
# DOYLIST = [str(x.timetuple().tm_yday) for x in dates_list]

DOYDICT = dict(zip(DOYLIST, unique_dates))

DOY2DATETIMEDICT = dict(zip(DOYLIST, df.reference_date.unique()))
DATETIME2DOYDICT = dict(zip(df.reference_date.unique(), DOYLIST))

# # For testing
# lc_options = [
#     {"label": str(NLCD_2011[lc_class]), "value": str(lc_class)} for lc_class in NLCD_2011
# ]

# df = pd.read_csv('data\\lcDF.csv', index_col=0, parse_dates=['variable'])
# df.columns = ['PointID', 'LC_code', 'reference_date', 'ndvi', 'lon', 'lat']
# df.info()

