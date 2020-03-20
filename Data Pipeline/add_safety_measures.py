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
        
# Create temp population column for complete_df
temp_complete_df = pd.merge(complete_df, populations_df, on="CountryName")


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
        
# Create temp population column for complete_df
temp_us_df = pd.merge(complete_df, us_df, on=["CountryName", "Region"])


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
        
# Create temp population column for complete_df
temp_china_df = pd.merge(complete_df, china_df, on="Region")


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
        
# Create temp population column for complete_df
temp_spain_df = pd.merge(complete_df, spain_df, on="Region")

# Combine all dataframes into one
temp_final_df = pd.concat([temp_complete_df, temp_us_df, temp_china_df, temp_spain_df], ignore_index=True)

# Delete duplicate rows
temp_final_df = temp_final_df.drop_duplicates(subset = None, keep = False)

# Sort dataframe by date
temp_final_df = temp_final_df.sort_values(['Date', 'CountryCode'], inplace=False)

# Add column for PercentConfirmed
temp_final_df["PercentConfirmed"] = None
for i in range(0, int(temp_final_df.shape[0])):
    percent_confirmed = (temp_final_df["Confirmed"][i]/temp_final_df["Population"][i]) * 100
    percent_confirmed = round(percent_confirmed,4)
    temp_final_df["PercentConfirmed"][i] = percent_confirmed

# Add 1 or 0 to SafetyMeasures column if threshold above 0.002 %
temp_final_df["SafetyMeasures"] = None
temp_final_df.loc[temp_final_df.PercentConfirmed >= 0.002, 'SafetyMeasures'] = 1
temp_final_df.loc[temp_final_df.PercentConfirmed < 0.002, 'SafetyMeasures'] = 0

# Save to CSV and JSON
temp_final_df.to_csv("Output_Data/complete_df_safety_measures.csv", index = False)
temp_final_df.to_json("Output_Data/complete_df_safety_measures.json", orient='records')