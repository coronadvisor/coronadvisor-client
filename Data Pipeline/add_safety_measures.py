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

# Remove US, Spain, China, Italy, and Australia from complete_df and put them into separate dataframes
complete_df_us = complete_df.loc[complete_df['CountryName'] == 'United States of America']
complete_df = complete_df[complete_df.CountryName != 'United States of America']

complete_df_spain = complete_df.loc[complete_df['CountryName'] == 'Spain']
complete_df = complete_df[complete_df.CountryName != 'Spain']

complete_df_china = complete_df.loc[complete_df['CountryName'] == 'China']
complete_df = complete_df[complete_df.CountryName != 'China']

complete_df_italy = complete_df.loc[complete_df['CountryName'] == 'Italy']
complete_df = complete_df[complete_df.CountryName != 'Italy']

complete_df_australia = complete_df.loc[complete_df['CountryName'] == 'Australia']
complete_df = complete_df[complete_df.CountryName != 'Australia']
      
# Get list of unique country names from complete_df and populations_df
unique_complete_df = complete_df['CountryName'].unique()
unique_complete_df = unique_complete_df.tolist()
unique_populations_df = populations_df['CountryName'].unique()
unique_populations_df = unique_populations_df.tolist()

# Find country names that show up in complete_df but not populations_df. Manually add missing populations to populations_df
world_missing = list(set(unique_complete_df) - set(unique_populations_df))
print("Regions with missing populations in complete_df: ")
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
        
# Get list of unique names
unique_complete_df_us = complete_df_us['Region'].unique()
unique_complete_df_us = unique_complete_df_us.tolist()
unique_populations_df_us = us_df['Region'].unique()
unique_populations_df_us = unique_populations_df_us.tolist()

# Find missing populations. Add manually
us_missing = list(set(unique_complete_df_us) - set(unique_populations_df_us))
print("Regions with missing populations in complete_df_us: ")
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

# Get list of unique names
unique_complete_df_china = complete_df_china['Region'].unique()
unique_complete_df_china = unique_complete_df_china.tolist()
unique_populations_df_china = china_df['Region'].unique()
unique_populations_df_china = unique_populations_df_china.tolist()

# Find missing populations. Add manually
china_missing = list(set(unique_complete_df_china) - set(unique_populations_df_china))
print("Regions with missing populations in complete_df_china: ")
for item in china_missing:
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

# Get list of unique names
unique_complete_df_spain = complete_df_spain['Region'].unique()
unique_complete_df_spain = unique_complete_df_spain.tolist()
unique_populations_df_spain = spain_df['Region'].unique()
unique_populations_df_spain = unique_populations_df_spain.tolist()

# Find missing populations. Add manually
spain_missing = list(set(unique_complete_df_spain) - set(unique_populations_df_spain))
print("Regions with missing populations in complete_df_spain: ")
for item in spain_missing:
    print(item)
        
# Create temp population column for complete_df
temp_spain_df = pd.merge(complete_df_spain, spain_df, on="Region")

############################################################################################################

# Add population of Italy regions
italy_df = pd.read_csv("Helper_Data/metadata_it.csv")

# Ensure columns are of type str and int
italy_df["Region"] = italy_df["Region"].astype(str)
i = 0
for item in italy_df["Population"]:
    temp = ''
    for c in str(item):
        if c != ',':
            temp += c
    italy_df["Population"][i] = temp
    i += 1
italy_df["Population"] = italy_df["Population"].astype(int)

# Get list of unique names
unique_complete_df_italy = complete_df_italy['Region'].unique()
unique_complete_df_italy = unique_complete_df_italy.tolist()
unique_populations_df_italy = italy_df['Region'].unique()
unique_populations_df_italy = unique_populations_df_italy.tolist()

# Find missing populations. Add manually
italy_missing = list(set(unique_complete_df_italy) - set(unique_populations_df_italy))
print("Regions with missing populations in complete_df_italy: ")
for item in italy_missing:
    print(item)
        
# Create temp population column for complete_df
temp_italy_df = pd.merge(complete_df_italy, italy_df, on="Region")

############################################################################################################

# Add population of Australia regions
australia_df = pd.read_csv("Helper_Data/metadata_au.csv")

# Ensure columns are of type str and int
australia_df["Region"] = australia_df["Region"].astype(str)
i = 0
for item in australia_df["Population"]:
    temp = ''
    for c in str(item):
        if c != ',':
            temp += c
    australia_df["Population"][i] = temp
    i += 1
australia_df["Population"] = australia_df["Population"].astype(int)

# Get list of unique names
unique_complete_df_australia = complete_df_australia['Region'].unique()
unique_complete_df_australia = unique_complete_df_australia.tolist()
unique_populations_df_australia = australia_df['Region'].unique()
unique_populations_df_australia = unique_populations_df_australia.tolist()

# Find missing populations. Add manually
australia_missing = list(set(unique_complete_df_australia) - set(unique_populations_df_australia))
print("Regions with missing populations in complete_df_australia: ")
for item in australia_missing:
    print(item)
        
# Create temp population column for complete_df
temp_australia_df = pd.merge(complete_df_australia, australia_df, on="Region")

############################################################################################################

# Combine all dataframes into one
temp_final_df = pd.concat([temp_complete_df, temp_us_df, temp_china_df, temp_spain_df, temp_italy_df, temp_australia_df], ignore_index=True)

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