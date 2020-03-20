* covid19_data_pipeline.py
  - Contains the program is used to scrape data from a variety of websites and save it all as formated CSV and JSON files
  - Websites scraped include:
    * European Centre for Disease Prevention and Control
      *   https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
    * The COVID Tracking Project
      * https://covidtracking.com/api/
    *  The world's largest online professional community of physicians, medical institutions, healthcare providers, and life science researchers.
       * http://www.dxy.cn/
    * The Spanish Minsitry of Health
      * https://www.mscbs.gob.es/en/home.htm
      
* add_safety_measures.py
  - Program that is used to add three columns into the CSV and JSON files containing all of the scraped data
  - Adds the columns: Population (number of people in country/region), PercentConfirmed (number of confirmed cases in country/region divided by population), and SafetyMeasures (0 if PercentConfirmed < 0.002, 1 if PercentConfirmed > 0.002)
  
* Helper_Data.zip
  - Contains all data files that are imported by convid19_data_pipeline.py and add_safety_measures.py
  - Neither one of the above programs can be run without saving all of the Helper Data files onto your device and importing them into each program 
  
* Output_Data.zip
  - All cleaned and formatted data returned from the web scrapes
  - complete_df.csv/.json
    - Contains nine columns: Date, Days Since 2019-12-31, CountryCode, CountryName, Region (region only included for the United States, China, and Spain. All other countries simply had their country name copied over into the 'Region' column), Confrimed, Deths, Latitude, and Longitude
  - complete_df_safety_measures.csv/.json
    - Contains the same nine columns as complete_df.csv/.json in addtion to the three columns created by 'add_safety_measures.py': Population, PercentConfrimed, SafetyMeasures
