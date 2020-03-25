##### PART 1: #####

# Crawling ECDC for global cases, excluding US and China

import httplib2
import bs4
import datetime
from bs4 import SoupStrainer
import pandas as pd
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
world_df = world_df[world_df.CountryName != 'Italy']
world_df = world_df[world_df.CountryName != 'Australia']

# Replace nan values with 0
value = 0
world_df['Deaths'] = world_df['Deaths'].fillna(value)
world_df['Confirmed'] = world_df['Confirmed'].fillna(value)

# Sort dataset by date
world_df = world_df.sort_values(['Date', 'CountryCode'])
world_df = world_df[['Date', 'Days Since 2019-12-31', 'CountryCode', 'CountryName', 'Region', 'Confirmed', 'Deaths', 'Latitude', 'Longitude']]





##### PART 3: #####

'''Credit to https://covidtracking.com/api/ for providing daily updates on US COVID19 cases'''

# Create dataframe for US cases by state
    
# Read JSON file from covidtracking's website
# We must use the requests package directly because covidtracking returns 403 otherwise
us_df = pd.read_json(requests.get(
    'https://covidtracking.com/api/states/daily', headers={'User-agent': 'Mozilla/5.0'}).text)


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
us_df = us_df.sort_values(['Date', 'Region'])





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

# Replace nan values with 0
value = 0
china_df['Deaths'] = china_df['Deaths'].fillna(value)
china_df['Confirmed'] = china_df['Confirmed'].fillna(value)

# Remove the time from the Date column, keeping only the date
china_df['Date'] = china_df['Date'].dt.date

# Sort dataset by date + region
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
china_df = china_df.sort_values(['Date', 'Region'])





##### PART 5: #####

'''Credit to https://github.com/open-covid-19 for scraping Spain data from MSCBS'''

# Download data.csv from COVID-19 GitHub and clean data
url = 'https://raw.githubusercontent.com/open-covid-19/data/master/output/data.csv'
spain_df = pd.read_csv(url)
del spain_df['RegionCode']

# Filter for only Spain
spain_df = spain_df.loc[spain_df['CountryName'] == 'Spain']

# Delete all rows that don't contain a region name
spain_df['RegionName'] = spain_df['RegionName'].fillna('null')
spain_df = spain_df.loc[spain_df['RegionName'] != 'null']

# Add in a column for days since 12/31/2019
basedate = pd.to_datetime('2019-12-31')
spain_df['Date'] = pd.to_datetime(spain_df['Date'])
spain_df['Days Since 2019-12-31'] = spain_df['Date'] - basedate
spain_df['Days Since 2019-12-31'] = spain_df['Days Since 2019-12-31'].fillna(0).astype(str)
spain_df['Days Since 2019-12-31'] = spain_df['Days Since 2019-12-31'].str.extract('(\d+)').astype(int) 

# Remove the time from the Date column, keeping only the date
spain_df['Date'] = spain_df['Date'].dt.date

# Rename RegionName column to Region
spain_df.rename(columns={'RegionName': 'Region'}, inplace=True)

# Replace nan values with 0
value = 0
spain_df['Deaths'] = spain_df['Deaths'].fillna(value)
spain_df['Confirmed'] = spain_df['Confirmed'].fillna(value)

# Sort dataset by date
spain_df = spain_df[['Date', 'Days Since 2019-12-31', 'CountryCode', 'CountryName', 'Region', 'Confirmed', 'Deaths', 'Latitude', 'Longitude']]
spain_df = spain_df.sort_values(['Date', 'CountryCode'])





##### PART 6: #####

'''Credit to https://github.com/open-covid-19 for scraping Italy data'''

# Download data.csv from COVID-19 GitHub and clean data
url = 'https://raw.githubusercontent.com/open-covid-19/data/master/output/data.csv'
italy_df = pd.read_csv(url)
del italy_df['RegionCode']

# Filter for only Italy
italy_df = italy_df.loc[italy_df['CountryName'] == 'Italy']

# Delete all rows that don't contain a region name
italy_df['RegionName'] = italy_df['RegionName'].fillna('null')
italy_df = italy_df.loc[italy_df['RegionName'] != 'null']

# Add in a column for days since 12/31/2019
basedate = pd.to_datetime('2019-12-31')
italy_df['Date'] = pd.to_datetime(italy_df['Date'])
italy_df['Days Since 2019-12-31'] = italy_df['Date'] - basedate
italy_df['Days Since 2019-12-31'] = italy_df['Days Since 2019-12-31'].fillna(0).astype(str)
italy_df['Days Since 2019-12-31'] = italy_df['Days Since 2019-12-31'].str.extract('(\d+)').astype(int) 

# Remove the time from the Date column, keeping only the date
italy_df['Date'] = italy_df['Date'].dt.date

# Rename RegionName column to Region
italy_df.rename(columns={'RegionName': 'Region'}, inplace=True)

value = 0
italy_df['Deaths'] = italy_df['Deaths'].fillna(value)
italy_df['Confirmed'] = italy_df['Confirmed'].fillna(value)

# Sort dataset by date
italy_df = italy_df[['Date', 'Days Since 2019-12-31', 'CountryCode', 'CountryName', 'Region', 'Confirmed', 'Deaths', 'Latitude', 'Longitude']]
italy_df = italy_df.sort_values(['Date', 'CountryCode'])





##### PART 7: #####

'''Credit to https://github.com/open-covid-19 for scraping Australia data'''

# Download data.csv from COVID-19 GitHub and clean data
url = 'https://raw.githubusercontent.com/open-covid-19/data/master/output/data.csv'
australia_df = pd.read_csv(url)
del australia_df['RegionCode']

# Filter for only Australia
australia_df = australia_df.loc[australia_df['CountryName'] == 'Australia']

# Delete all rows that don't contain a region name
australia_df['RegionName'] = australia_df['RegionName'].fillna('null')
australia_df = australia_df.loc[australia_df['RegionName'] != 'null']

# Add in a column for days since 12/31/2019
basedate = pd.to_datetime('2019-12-31')
australia_df['Date'] = pd.to_datetime(australia_df['Date'])
australia_df['Days Since 2019-12-31'] = australia_df['Date'] - basedate
australia_df['Days Since 2019-12-31'] = australia_df['Days Since 2019-12-31'].fillna(0).astype(str)
australia_df['Days Since 2019-12-31'] = australia_df['Days Since 2019-12-31'].str.extract('(\d+)').astype(int) 

# Remove the time from the Date column, keeping only the date
australia_df['Date'] = australia_df['Date'].dt.date

# Rename RegionName column to Region
australia_df.rename(columns={'RegionName': 'Region'}, inplace=True)

value = 0
australia_df['Deaths'] = australia_df['Deaths'].fillna(value)
australia_df['Confirmed'] = australia_df['Confirmed'].fillna(value)

# Sort dataset by date
australia_df = australia_df[['Date', 'Days Since 2019-12-31', 'CountryCode', 'CountryName', 'Region', 'Confirmed', 'Deaths', 'Latitude', 'Longitude']]
australia_df = australia_df.sort_values(['Date', 'CountryCode'])





##### PART 8: #####
'''
Only needs to be executed the very first time the program is run.
From the first time onwards, you do not need to re-save the complete_df to your directory. It will already be saved.
You will simply be adding the latest days data to the complete_df, then writing the updated version over the old one.
'''

# Combine all data into one dataframe 
complete_df = pd.DataFrame
complete_df = pd.concat([world_df, us_df, china_df, spain_df, italy_df, australia_df], ignore_index=True)

# Sort dataset by date
complete_df = complete_df.sort_values(['Date', 'CountryCode'])

# Save complete dataset in CSV and JSON format into output folder
complete_df.to_csv('Output_Data/complete_df.csv', index=False)
complete_df.to_json('Output_Data/complete_df.json', orient='records')





##### PART 9: #####

# Adding new day's data to the complete dataframe

# Extract a subset with only the most recent date from world_df
world_df_latest = pd.DataFrame(columns=list(world_df.columns))
world_df_latest_date = world_df['Date'].max()
world_df_latest = world_df.loc[world_df['Date'] == world_df_latest_date]
    
# Extract a subset with only the latest date from us_df
us_df_latest = pd.DataFrame(columns=list(us_df.columns))
us_df_latest_date = us_df['Date'].max()
us_df_latest = us_df.loc[us_df['Date'] == us_df_latest_date]
    
# Extract a subset with only the latest date from china_df
china_df_latest = pd.DataFrame(columns=list(china_df.columns))
china_df_latest_date = china_df['Date'].max()
china_df_latest = china_df.loc[china_df['Date'] == china_df_latest_date]
    
# Extract a subset with only the most recent data from spain_df
spain_df_latest = pd.DataFrame(columns=list(spain_df.columns))
spain_df_latest_date = spain_df['Date'].max()
spain_df_latest = spain_df.loc[spain_df['Date'] == spain_df_latest_date]

# Extract a subset with only the most recent data from italy_df
italy_df_latest = pd.DataFrame(columns=list(italy_df.columns))
italy_df_latest_date = italy_df['Date'].max()
italy_df_latest = italy_df.loc[italy_df['Date'] == italy_df_latest_date]

# Extract a subset with only the most recent data from australia_df
australia_df_latest = pd.DataFrame(columns=list(australia_df.columns))
australia_df_latest_date = australia_df['Date'].max()
australia_df_latest = australia_df.loc[australia_df['Date'] == australia_df_latest_date]   
    
# Import yesterday's data
old_df = pd.read_csv('Output_Data/complete_df.csv')

# Change format of date column in odl_df to match date format in new_df
old_df['Date'] = pd.to_datetime(old_df['Date'])
old_df['Date'] = old_df['Date'].dt.date

# Create updated dataframe
new_df = pd.concat([world_df_latest, old_df, us_df_latest, spain_df_latest, china_df_latest, italy_df_latest, australia_df_latest], ignore_index=True)
new_df['Date'] = pd.to_datetime(new_df['Date'])
new_df['Date'] = new_df['Date'].dt.date

# Ensure all column types in new_df and old_df are of same type (for comparission)
old_df['Date'] = old_df['Date'].astype(str)
new_df['Date'] = new_df['Date'].astype(str)

old_df['Days Since 2019-12-31'] = old_df['Days Since 2019-12-31'].astype(int)
new_df['Days Since 2019-12-31'] = new_df['Days Since 2019-12-31'].astype(int)

old_df['CountryCode'] = old_df['CountryCode'].astype(str)
new_df['CountryCode'] = new_df['CountryCode'].astype(str)

old_df['CountryName'] = old_df['CountryName'].astype(str)
new_df['CountryName'] = new_df['CountryName'].astype(str)

old_df['Region'] = old_df['Region'].astype(str)
new_df['Region'] = new_df['Region'].astype(str)

old_df['Confirmed'] = old_df['Confirmed'].astype(int)
new_df['Confirmed'] = new_df['Confirmed'].astype(int)

old_df['Deaths'] = old_df['Deaths'].astype(int)
new_df['Deaths'] = new_df['Deaths'].astype(int)

old_df['Latitude'] = old_df['Latitude'].astype(float)
new_df['Latitude'] = new_df['Latitude'].astype(float)

old_df['Longitude'] = old_df['Longitude'].astype(float)
new_df['Longitude'] = new_df['Longitude'].astype(float)

# Round all lats and lngs to 4 decimal places or Pandas won't be able to properly compare values
old_df['Latitude'] = old_df['Latitude'].apply(lambda x: round(x, 4))
new_df['Latitude'] = new_df['Latitude'].apply(lambda x: round(x, 4))
old_df['Longitude'] = old_df['Longitude'].apply(lambda x: round(x, 4))
new_df['Longitude'] = new_df['Longitude'].apply(lambda x: round(x, 4))

# Delete duplicate rows
new_df = new_df.drop_duplicates(subset = None, keep = 'first', inplace = False)

# Sort dataframe by date
new_df = new_df.sort_values(['Date', 'CountryCode'], inplace=False)

# Save complete dataset in CSV and JSON format into output folder
new_df.to_csv('Output_Data/complete_df.csv', index=False)
new_df.to_json('Output_Data/complete_df.json', orient='records')

# =============================================================================
# # Save most recent day's dataset in CSV and JSON format into output folder (OPTIONAL)
# latest_df = pd.concat([us_df_latest, china_df_latest, world_df_latest, spain_df_latest], ignore_index=True)
# latest_df.to_csv('latest_data.csv', index=False)
# latest_df.to_json('latest_data.json', orient='records')
# =============================================================================