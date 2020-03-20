##### PART 1: #####

'''Credit https://github.com/open-covid-19 for providing framework for live data collection and reliable COVID19-reporting websites'''

# Crawling ECDC for global cases, excluding US and China

import httplib2
import bs4
import datetime
from bs4 import SoupStrainer
import pandas as pd
import numpy as np
import re
import requests

# ECDC website
url = 'https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide'

# Finding link to download the .xlsx file
http = httplib2.Http()
status, response = http.request(url)
links = []

for link in bs4.BeautifulSoup(response, 'html.parser', parseOnlyThese=SoupStrainer('a')):
    if link.has_attr('href'):
        links.append(link['href'])
      
updated = []
for link in links:
    if re.match(r'.*.xls', link):
        updated.append(link)
        links = sorted(links, key=lambda x: x.split('/')[-1])
        break
        
# Saving .xlsx file
resp = requests.get(updated[0])

current_date = datetime.datetime.today().strftime('%Y-%m-%d')
output = open(f'Helper_Data/ecdc_daily_world_data/COVID-19-geographic-disbtribution-worldwide-{current_date}.xlsx', 'wb')
output.write(resp.content)
output.close()
      
  

##### PART 2: #####

# Parsing ECDC to create dataframe for global cases, excluding US and China

# Read XLSX file
world_df = pd.read_excel(f'Helper_Data/ecdc_daily_world_data/COVID-19-geographic-disbtribution-worldwide-{current_date}.xlsx')
world_df = world_df.sort_values(['DateRep', 'GeoId'])

# Convert dates to string
world_df['DateRep'] = world_df['DateRep'].astype(str)

# ECDC mistakenly labels Greece country code as EL instead of GR
world_df['GeoId'] = world_df['GeoId'].apply(lambda code: 'GR' if code == 'EL' else code)

# ECDC mistakenly labels United Kingdom country code as UK instead of GB
world_df['GeoId'] = world_df['GeoId'].apply(lambda code: 'GB' if code == 'UK' else code)

# Compute the cumsum of values
columns = ['DateRep', 'GeoId', 'Confirmed', 'Deaths']
world_df_ = pd.DataFrame(columns=columns)
for country in world_df['GeoId'].unique():
    subset = world_df[world_df['GeoId'] == country].copy()
    subset['Confirmed'] = subset['Cases'].cumsum()
    subset['Deaths'] = subset['Deaths'].cumsum()
    world_df_ = pd.concat([world_df_, subset[columns]])

world_df_ = world_df_[columns]
world_df_.columns = ['Date', 'CountryCode', 'Confirmed', 'Deaths']
world_df = world_df_

# Make sure all data types are appropriately casted
world_df['Confirmed'] = world_df['Confirmed'].fillna(0).astype(int)
world_df['Deaths'] = world_df['Deaths'].fillna(0).astype(int)

# Temporary workaround for https://github.com/open-covid-19/data/issues/12
# ECDC reported only 90 new cases for Italy, which is clearly wrong. For all
# other days, it appears to report only active cases so we are reporting
# today's active case count from the local official source to avoid a sudden
# jump in the data but this will be fixed retroactively
# https://web.archive.org/web/20200316021137/http://www.salute.gov.it/nuovocoronavirus
world_df = world_df.set_index(['Date', 'CountryCode'])
world_df.loc[('2020-03-15', 'IT'), 'Confirmed'] = 20603
world_df = world_df.reset_index()

# Load coordinates and names for each country
# Data from: https://developers.google.com/public-data/docs/canonical/countries_csv
world_df = world_df.merge(pd.read_csv('Helper_Data/country_coordinates.csv', dtype=str))

# Add in a column for days since 12/31/2019
basedate = pd.to_datetime('2019-12-31')
world_df['Date'] = pd.to_datetime(world_df['Date'])
world_df['Days Since 2019-12-31'] = world_df['Date'] - basedate
world_df['Days Since 2019-12-31'] = world_df['Days Since 2019-12-31'].fillna(0).astype(str)
world_df['Days Since 2019-12-31'] = world_df['Days Since 2019-12-31'].str.extract('(\d+)').astype(int) 

# Create column for region (just copies the country name into the region column except for US and China)
world_df['Region'] = world_df['CountryName']

# Remove the time from the Date column, keeping only the date
world_df['Date'] = world_df['Date'].dt.date

# Delete rows containing US, China, and Spain so they can be re-added with regions
world_df = world_df[world_df.CountryName != 'China']
world_df = world_df[world_df.CountryName != 'United States of America']
world_df = world_df[world_df.CountryName != 'Spain']


# Sort dataset by date
world_df = world_df.sort_values(['Date', 'CountryCode'])
world_df = world_df[['Date', 'Days Since 2019-12-31', 'CountryCode', 'CountryName', 'Region', 'Confirmed', 'Deaths', 'Latitude', 'Longitude']]

# Replace nan values with 0
value = 0
world_df['Deaths'] = world_df['Deaths'].fillna(value)
world_df['Confirmed'] = world_df['Confirmed'].fillna(value)



##### PART 3: #####

'''Credit to https://covidtracking.com/api/ for providing daily updates on US COVID19 cases'''

# Create dataframe for US cases by state
    
# Read JSON file from covidtracking's website
# We must use the requests package directly because covidtracking returns 403 otherwise
us_df = pd.read_json(requests.get(
    'http://covidtracking.com/api/states/daily', headers={'User-agent': 'Mozilla/5.0'}).text)


# Rename the appropriate columns
us_df = us_df.rename(columns={
    'date': 'Date',
    'state': 'Region',
    'positive': 'Confirmed', 
    'death': 'Deaths', 
    'total': 'Tested'
})

# Make sure all numbers are string objects
for col in ('Confirmed', 'Deaths', 'Tested'):
    us_df[col] = us_df[col].dropna().astype(int).astype(str)
    
# Replace nan values with 0
value = 0
us_df['Deaths'] = us_df['Deaths'].fillna(value)
us_df['Confirmed'] = us_df['Confirmed'].fillna(value)

# Convert date to ISO format
us_df['Date'] = us_df['Date'].apply(
    lambda date: datetime.datetime.strptime(str(date), '%Y%m%d').strftime('%Y-%m-%d'))

# Add in a column for days since 12/31/2019
basedate = pd.to_datetime('2019-12-31')
us_df['Date'] = pd.to_datetime(us_df['Date'])
us_df['Days Since 2019-12-31'] = us_df['Date'] - basedate
us_df['Days Since 2019-12-31'] = us_df['Days Since 2019-12-31'].fillna(0).astype(str)
us_df['Days Since 2019-12-31'] = us_df['Days Since 2019-12-31'].str.extract('(\d+)').astype(int)

# Remove the time from the Date column, keeping only the date
us_df['Date'] = us_df['Date'].dt.date

# Get the coordinates for each region
us_df = us_df.merge(pd.read_csv('Helper_Data/usa_regions.csv'))
us_df['CountryName'] = 'United States of America'

# Sort dataset by date
us_df = us_df.sort_values(['Date', 'Region'])
us_df = us_df[[
    'Date',
    'Days Since 2019-12-31',
    'CountryCode', 
    'CountryName', 
    'Region',
    'Confirmed', 
    'Deaths', 
    'Latitude', 
    'Longitude',
]]



##### PART 4 #####
    
'''Credit to the github.com/BlankerL team for scraping the data from DXY.cn.'''

# Read DXY CSV file from  website
china_df = pd.read_csv('https://raw.githubusercontent.com/BlankerL/DXY-COVID-19-Data/master/csv/DXYArea.csv')

# Since all other reporting is done at 10 AM GMT+1, adjust for timezone difference
def timezone_adjust(time: str):
    ''' Adjust 7 hour difference between China's GMT+8 and GMT+1 '''
    timestamp = datetime.datetime.fromisoformat(time)
    if timestamp.hour <= 24 - 7:
        return timestamp.date().isoformat()
    else:
        return (timestamp + datetime.timedelta(days=1)).date().isoformat()

china_df['Date'] = china_df['updateTime'].apply(timezone_adjust)

# Rename the appropriate columns
china_df = china_df.rename(columns={
    'countryEnglishName': 'CountryName',
    'provinceEnglishName': 'Region',
    'province_confirmedCount': 'Confirmed', 
    'province_deadCount': 'Deaths', 
    'province_curedCount': 'Recovered'
})

# This is time series data, get only the last snapshot of each day
china_df = china_df.sort_values('Date').groupby(['Date', 'CountryName', 'Region']).last().reset_index()

# Get the coordinates for each region
china_df = china_df[china_df['CountryName'] == 'China'].merge(
    pd.read_csv('Helper_Data/china_regions.csv', dtype=str), on='Region')

# Add in a column for days since 12/31/2019
basedate = pd.to_datetime('2019-12-31')
china_df['Date'] = pd.to_datetime(china_df['Date'])
china_df['Days Since 2019-12-31'] = china_df['Date'] - basedate
china_df['Days Since 2019-12-31'] = china_df['Days Since 2019-12-31'].fillna(0).astype(str)
china_df['Days Since 2019-12-31'] = china_df['Days Since 2019-12-31'].str.extract('(\d+)').astype(int)

# Sort dataset by date + region
china_df = china_df.sort_values(['Date', 'Region'])
china_df = china_df[[
    'Date', 
    'Days Since 2019-12-31',
    'CountryCode', 
    'CountryName', 
    'Region',
    'Confirmed', 
    'Deaths', 
    'Latitude', 
    'Longitude'
]]

# Replace nan values with 0
value = 0
china_df['Deaths'] = china_df['Deaths'].fillna(value)
china_df['Confirmed'] = china_df['Confirmed'].fillna(value)

# Remove the time from the Date column, keeping only the date
china_df['Date'] = china_df['Date'].dt.date



##### PART 5: #####

# Download spain.csv from COVID-19 GitHub and clean data




##### PART 6: #####
'''
Only needs to be executed the very first time the program is run.
From the first time onwards, you do not need to re-save the complete_df to your directory. It will already be saved.
You will simply be adding the latest days data to the complete_df, then writing the updated version over the old one.
'''

# =============================================================================
# # Combine all data into one dataframe 
# complete_df = pd.DataFrame
# complete_df = pd.concat([us_df, china_df, world_df], ignore_index=True)
# 
# # Sort dataset by date
# complete_df = complete_df.sort_values(['Date', 'CountryCode'])
# 
# # Dropping duplicates
# complete_df = complete_df.drop_duplicates(keep=False)
# 
# # Save complete dataset in CSV and JSON format into output folder
# complete_df.to_csv('Output_Data/complete_df.csv', index=False)
# complete_df.to_json('Output_Data/complete_df.json', orient='records')
# =============================================================================


##### PART 7: #####

# Adding new day's data to the complete dataframe

# Extract a subset with only the most recent data from world_df
world_df_latest = pd.DataFrame(columns=list(world_df.columns))
for country in world_df['CountryCode'].unique():
    world_df_latest = pd.concat([world_df_latest, world_df[world_df['CountryCode'] == country].iloc[-1:]])
    
# Extract a subset with only the latest date from us_df
us_df_latest = pd.DataFrame(columns=list(us_df.columns))
for country in us_df['Region'].unique():
    us_df_latest = pd.concat([us_df_latest, us_df[us_df['Region'] == country].iloc[-1:]])
    
# Extract a subset with only the latest date from china_df
china_df_latest = pd.DataFrame(columns=list(china_df.columns))
for region in sorted(china_df['Region'].unique()):
    china_df_latest = pd.concat([china_df_latest, china_df[china_df['Region'] == region].iloc[-1:]])
    
# Add latest data to current data
old_df = pd.read_csv('Output_Data/complete_df.csv')

# Change format of date column in odl_df to match date format in new_df
old_df['Date'] = pd.to_datetime(old_df['Date'])
old_df['Date'] = old_df['Date'].dt.date

# Create updated dataframe
new_df = pd.concat([old_df, us_df_latest, china_df_latest, world_df_latest], ignore_index=True)

# Delete duplicate rows
new_df = new_df.drop_duplicates(subset = None, keep = False)
# Sort dataframe by date
new_df = new_df.sort_values(['Date', 'CountryCode'], inplace=False)

# Save complete dataset in CSV and JSON format into output folder
new_df.to_csv('Output_Data/complete_df.csv', index=False)
new_df.to_json('Output_Data/complete_df.json', orient='records')

# =============================================================================
# # Save most recent day's dataset in CSV and JSON format into output folder (OPTIONAL)
# latest_df = pd.concat([us_df_latest, china_df_latest, world_df_latest], ignore_index=True)
# latest_df.to_csv('latest_data.csv', index=False)
# latest_df.to_json('latest_data.json', orient='records')
# =============================================================================