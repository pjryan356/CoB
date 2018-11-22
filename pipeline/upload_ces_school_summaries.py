## Load School summaries data excel files downloaded from Survey Team google drive
# Peter Ryan October 2018

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


def upload_school_data_from_excel(directory, filename, engine,
                                  school_tbl_name='tbl_school_post2017',
                                  college_tbl_name='tbl_college_post2017',
                                  schema='ces'):
  # gets course ces data split by program from the suuplied excel files and uploads them to postrgres

  f_split = filename.split('.')[0].split('_')
  
  level = f_split[5]
  semester = int(f_split[4][1:]) # S removed
  year = int(f_split[3])
  
  if year < 2018:
    df = pd.read_excel(directory + filename,
                     sheet_name='Sheet1',
                     skiprows=4,
                     usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
                     skipfooter=6)

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
    df = pd.read_excel(directory + filename,
                       sheet_name='Sheet1',
                       skiprows=4,
                       usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                       skipfooter=6)

    df.columns = ['school_extra',
                  'population', 'osi_count', 'gts_count', 'reliability',
                  'gts', 'gts_mean', 'osi', 'osi_mean',
                  'int', 'dom', 'ft', 'pt',
                  'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']

  # Remove non data rows
  df = df.loc[df['osi_count'].notna()]
  
  df['year'] = int(year)
  df['semester'] = int(semester)
  df['level'] = level
  
  # create school column
  temp = df['school_extra'].str.split('-', n=1, expand=True)
  df['school_code'] = temp[0]
  df.drop(columns=["school_extra"], inplace=True)

  #Reorder columns
  df = df[['year', 'semester', 'level', 'school_code',
           'population', 'osi_count', 'gts_count', 'reliability',
           'gts', 'gts_mean', 'osi', 'osi_mean',
           'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']]
  
  #### up to here
  df = df.infer_objects()
  
  df[['gts', 'gts_mean', 'osi', 'osi_mean',
      'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']] \
    = df[['gts', 'gts_mean', 'osi', 'osi_mean',
          'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']].apply(pd.to_numeric, errors='coerce')
  
  df = df.loc[df['osi_count'].notna()]
  
  #split into school, college/university
  df_school = df.loc[df['school_code'].str[0].str.isnumeric()==True]
  df_college = df.loc[df['school_code'].str[0].str.isnumeric()==False]

  df_college['college']=df['school_code']
  df_college = df_college[['year', 'semester', 'level', 'college',
           'population', 'osi_count', 'gts_count', 'reliability',
           'gts', 'gts_mean', 'osi', 'osi_mean',
           'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']]
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

# get data from excel doc
# open template
directory = 'H:\\Data\\CoB Database\\CES\\School_summaries\\'

for filename in os.listdir(directory):
    if filename.endswith(".xls"):
        print(os.path.join(directory, filename))
        upload_school_data_from_excel(directory, filename, postgres_engine)
        continue
    else:
        continue

