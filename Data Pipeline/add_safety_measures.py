# Date of safety measure implimentation

import pandas as pd

complete_df = pd.read_csv("Output_Data/complete_df.csv")
populations_df = pd.read_csv("Helper_Data/country_populations.csv", encoding='ISO-8859-1')


# Ensure columns are of type str and int
populations_df["CountryName"] = populations_df["CountryName"].astype(str)
i = 0
for item in populations_df["Population"]:
    temp = ''
    for c in item:
        if c != ',':
            temp += c
    populations_df["Population"][i] = temp
    i += 1
populations_df["Population"] = populations_df["Population"].astype(int)

# Remove US, Spain, and China from complete_df and put them into separate dataframes
complete_df_us = complete_df.loc[complete_df['CountryName'] == 'United States of America']
complete_df = complete_df[complete_df.CountryName != 'United States of America']

complete_df_spain = complete_df.loc[complete_df['CountryName'] == 'Spain']
complete_df = complete_df[complete_df.CountryName != 'Spain']

complete_df_china = complete_df.loc[complete_df['CountryName'] == 'China']
complete_df = complete_df[complete_df.CountryName != 'China']
      
# Get list of unique country names from complete_df and populations_df
unique_complete_df = complete_df['CountryName'].unique()
unique_complete_df = unique_complete_df.tolist()
unique_populations_df = populations_df['CountryName'].unique()
unique_populations_df = unique_populations_df.tolist()

# Find country names that show up in complete_df but not populations_df. Manually add missing populations to populations_df
world_missing = list(set(unique_complete_df) - set(unique_populations_df))
for item in world_missing:
    print(item)
    
# Create temp population column for complete_df
temp_complete_df = pd.merge(complete_df, populations_df, on="CountryName")

############################################################################################################

# Add Population of US states
us_df = pd.read_csv("Helper_Data/us_states_population.csv", encoding='ISO-8859-1')

# Ensure columns are of type str and int
us_df["Region"] = us_df["Region"].astype(str)
i = 0
for item in us_df["Population"]:
    temp = ''
    for c in item:
        if c != ',':
            temp += c
    us_df["Population"][i] = temp
    i += 1
us_df["Population"] = us_df["Population"].astype(int)
        
# Create list of all unique US state names that show up in complete_df and in us_df
unique_us_states_complete_df = complete_df.loc[complete_df['CountryName'] == 'United States of America']
unique_us_states_complete_df = unique_us_states_complete_df['Region'].unique()
unique_us_states_complete_df = unique_us_states_complete_df.tolist()
unique_states_us_df = us_df['Region'].unique()
unique_states_us_df = unique_states_us_df.tolist()

# Find country names that show up in unique_us_states_complete_df but not unique_states_us_df. Manually add missing populations to us_df
us_missing = list(set(unique_us_states_complete_df) - set(unique_states_us_df))
for item in us_missing:
    print(item)

# Create temp population column for complete_df
temp_us_df = pd.merge(complete_df_us, us_df, on=["CountryName", "Region"])

############################################################################################################

# Add population of Chinese provinces
china_df = pd.read_csv("Helper_Data/china_province_population.csv")

# Ensure columns are of type str and int
china_df["Region"] = china_df["Region"].astype(str)
i = 0
for item in china_df["Population"]:
    temp = ''
    for c in item:
        if c != ',':
            temp += c
    china_df["Population"][i] = temp
    i += 1
china_df["Population"] = china_df["Population"].astype(int)

# Create list of all unique Chinese province names that show up in complete_df and in china_df
unique_china_provinces_complete_df = complete_df.loc[complete_df['CountryName'] == 'China']
unique_china_provinces_complete_df = unique_china_provinces_complete_df['Region'].unique()
unique_china_provinces_complete_df = unique_china_provinces_complete_df.tolist()
unique_provinces_china_df = china_df['Region'].unique()
unique_provinces_china_df = unique_provinces_china_df.tolist()

# Find country names that show up in unique_china_provinces_complete_df but not unique_provinces_china_df. Manually add missing populations to us_df
china_provinces_missing = list(set(unique_china_provinces_complete_df) - set(unique_provinces_china_df))
for item in china_provinces_missing:
    print(item)
        
# Create temp population column for complete_df
temp_china_df = pd.merge(complete_df_china, china_df, on="Region")

############################################################################################################

# Add population of Spain regions
spain_df = pd.read_csv("Helper_Data/spain_region_population.csv")

# Ensure columns are of type str and int
spain_df["Region"] = spain_df["Region"].astype(str)
i = 0
for item in spain_df["Population"]:
    temp = ''
    for c in item:
        if c != ',':
            temp += c
    spain_df["Population"][i] = temp
    i += 1
spain_df["Population"] = spain_df["Population"].astype(int)

# Create list of all unique Spanish region names that show up in complete_df and in spain_df
unique_spain_regions_complete_df = complete_df.loc[complete_df['CountryName'] == 'Spain']
unique_spain_regions_complete_df =unique_spain_regions_complete_df['Region'].unique()
unique_spain_regions_complete_df = unique_spain_regions_complete_df.tolist()
unique_regions_spain_df = spain_df['Region'].unique()
unique_regions_spain_df = unique_regions_spain_df.tolist()

# Find country names that show up in unique_spain_regions_complete_df but not unique_regions_spain_df. Manually add missing populations to us_df
spain_regions_missing = list(set(unique_spain_regions_complete_df) - set(unique_regions_spain_df))
for item in spain_regions_missing:
    print(item)
        
# Create temp population column for complete_df
temp_spain_df = pd.merge(complete_df_spain, spain_df, on="Region")


# Combine all dataframes into one
temp_final_df = pd.concat([temp_us_df, temp_china_df, temp_spain_df, temp_complete_df, ], ignore_index=True)

# Ensure all values in columns are of same type (for comparission)
temp_final_df['Date'] = temp_final_df['Date'].astype(str)

temp_final_df['Days Since 2019-12-31'] = temp_final_df['Days Since 2019-12-31'].astype(int)

temp_final_df['CountryCode'] = temp_final_df['CountryCode'].astype(str)

temp_final_df['CountryName'] = temp_final_df['CountryName'].astype(str)

temp_final_df['Region'] = temp_final_df['Region'].astype(str)

temp_final_df['Confirmed'] = temp_final_df['Confirmed'].astype(int)

temp_final_df['Deaths'] = temp_final_df['Deaths'].astype(int)

temp_final_df['Latitude'] = temp_final_df['Latitude'].astype(float)

temp_final_df['Longitude'] = temp_final_df['Longitude'].astype(float)

# Round all lats and lngs to 4 decimal places or Pandas won't be able to properly compare values
temp_final_df['Latitude'] = temp_final_df['Latitude'].apply(lambda x: round(x, 4))
temp_final_df['Longitude'] = temp_final_df['Longitude'].apply(lambda x: round(x, 4))

# Delete duplicate rows (shouldn't be any but here just for safety)
temp_final_df = temp_final_df.drop_duplicates(subset = None, keep = 'first')

# Add column for PercentConfirmed
temp_final_df["PercentConfirmed"] = None

for z in range(0, int(temp_final_df.shape[0])):
    percent_confirmed = (temp_final_df['Confirmed'][z] / temp_final_df['Population'][z])*100
    percent_confirmed = round(percent_confirmed, 4)
    temp_final_df['PercentConfirmed'][z] = percent_confirmed

# Add 1 or 0 to SafetyMeasures column if threshold above 0.002 %
temp_final_df["SafetyMeasures"] = None
temp_final_df.loc[temp_final_df.PercentConfirmed >= 0.002, 'SafetyMeasures'] = 1
temp_final_df.loc[temp_final_df.PercentConfirmed < 0.002, 'SafetyMeasures'] = 0

# Sort dataframe by date
temp_final_df = temp_final_df.sort_values(['Date', 'CountryCode'], inplace=False)

# Save to CSV and JSON
temp_final_df.to_csv("Output_Data/complete_df_safety_measures.csv", index = False)
temp_final_df.to_json("Output_Data/complete_df_safety_measures.json", orient='records')