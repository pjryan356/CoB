'''
Load CES school and college data
  - from excel files downloaded from Survey Team google drive
  - into Local postgres Database
      - ces.tbl_school_mean
      - ces.tbl_college_mean

First download VE & HE files from google drive into 'directory' and
if necessary update line 40 directory =
  - currently two separate file sets (PA and Mean) are received.
  - ensure that only Mean files are in directory
  - there is a separate script to load the Mean files
  - ensure that the file format (columns etc.) has not changed before running this script
  - ensure that filename format has not changed

Peter Ryan April 2020
'''

import os
import pandas as pd
import psycopg2
from tabulate import tabulate
from sqlalchemy import (create_engine, orm)

# Create connections
# create postgres engine this is the connection to the oracle database
postgres_user = 'pjryan'
postgres_host = 'localhost'
postgres_dbname = 'postgres'
postgres_pw = input("Postgres Password: ")

engine_string = 'postgresql+psycopg2://{}:{}@{}/{}'.format(postgres_user,
                                                           postgres_pw,
                                                           postgres_host,
                                                           postgres_dbname)
postgres_engine = create_engine(engine_string)
postgres_con = postgres_engine.connect()


# Directory containing files
directory = 'H:\\Data\\CoB Database\\CES\\2020S1\\School\\'


# Function to load:
#   - School data; and
#   - College data;
# into database
def upload_school_data_from_excel(directory, filename, engine,
                                  school_tbl_name='tbl_school_means',
                                  college_tbl_name='tbl_college_means',
                                  schema='ces'):
  # Gather information (year, semester, level) from the filename
  'CES Whole School Mean Summary (HE) RMIT (Semester 1, 2020)'
  
  f_split = filename.split('.')[0].split(' ')
  
  level = f_split[5][1:-1] # () removed
  semester = int(f_split[8][:-1]) # , removed
  year = int(f_split[9][:-1]) # removed )

  # Load all data from filename
  # The first 4 rows are headers and hence are skipped
  # The last 6 rows are ignored (This is probably redundant)

  # Data includes three levels of aggregation:
  #   - School; and
  #   - College; and
  #   - RMIT (RMIT data is placed into the college table)

  # The School data is deteremined by the school codes first element being a numeral
  # The College/RMIT data is deteremined by the school codes first element not being a numeral
  
  if year < 2018:
    df = pd.read_excel(directory + filename,
                     sheet_name='Sheet1',
                     skiprows=4,
                     usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
                     skipfooter=0)

    df.columns = ['school_extra',
                  'population', 'osi_count', 'gts_count', 'reliability',
                  'gts', 'osi',
                  'int', 'dom', 'ft', 'pt',
                  'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']

    df['osi_mean'] = None
    df['gts_mean'] = None
    
    df = df[['school_extra',
             'population', 'osi_count', 'gts_count', 'reliability',
             'gts', 'gts_mean', 'osi', 'osi_mean',
             'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']]


  if year >= 2018:
    # Load data
    df = pd.read_excel(directory + filename,
                       sheet_name='Sheet1',
                       skiprows=4,
                       usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                       skipfooter=6)
    
    # Rename columns
    df.columns = ['school_extra',
                  'population', 'osi_count', 'gts_count', 'reliability',
                  'gts', 'mgts', 'osi', 'mosi',
                  'int', 'dom', 'ft', 'pt',
                  'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']

  # Remove rows with no data
  df = df.loc[df['osi_count'].notna()]
  
  df['year'] = int(year)
  df['semester'] = int(semester)
  df['level'] = level
  
  # create school column
  temp = df['school_extra'].str.split('-', n=1, expand=True)
  df['school_code'] = temp[0]
  df.drop(columns=["school_extra"], inplace=True)

  #Reorder columns and remove int, dom, ft, pt
  df = df[['year', 'semester', 'level', 'school_code',
           'population', 'osi_count', 'gts_count', 'reliability',
           'gts', 'mgts', 'osi', 'mosi',
           'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']]
  
  # Correct data types
  df = df.infer_objects()
  
  df[['gts', 'mgts', 'osi', 'mosi',
      'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']] \
    = df[['gts', 'mgts', 'osi', 'mosi',
          'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']].apply(pd.to_numeric, errors='coerce')
  
  df = df.loc[df['osi_count'].notna()]
  
  # Seperate into:
  #   - School data; (if first element of text in school_code is a numeral)
  #   - College/RMIT data (if first element of text in school code is a not a numeral);
  
  df_school = df.loc[df['school_code'].str[0].str.isnumeric()==True]
  df_college = df.loc[df['school_code'].str[0].str.isnumeric()==False]
  
  # Change school code in college in college data
  df_college['college'] = df_college['school_code']
  df_college = df_college[['year', 'semester', 'level', 'college',
           'population', 'osi_count', 'gts_count', 'reliability',
           'gts', 'mgts', 'osi', 'mosi',
           'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']]

  # Load School data into database
  try:
    df_school.to_sql(
      name=school_tbl_name,
      con=engine,
      schema=schema,
      if_exists='append',
      index=False
    )
  except:
    print(filename)
    #print(df)
    pass

  # Load College data into database
  try:
    df_college.to_sql(
      name=college_tbl_name,
      con=engine,
      schema=schema,
      if_exists='append',
      index=False
    )
  except:
    print(filename)
    pass


for filename in os.listdir(directory):
    if filename.endswith(".xls"):
        print(os.path.join(directory, filename))
        upload_school_data_from_excel(directory, filename, postgres_engine)
        continue
    else:
        continue

