## Load CES course_program data excel files downloaded from Survey Team google drive
# Peter Ryan October 2018

import os
import pandas as pd
import psycopg2
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


def upload_course_prog_data_from_excel(directory, filename, engine, tbl_name='tbl_course_program_post2018', schema='ces'):
  # gets course ces data split by program from the suuplied excel files and uploads them to postrgres
  df = pd.read_excel(directory + filename,
                     sheet_name='Sheet1',
                     skiprows=4,
                     usecols=[0,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25],
                     skipfooter=15)
  
  df.columns = ['program_code',  'population', 'osi_count', 'gts_count', 'reliability',
                'gts', 'gts_mean', 'osi', 'osi_mean',
                'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6',
                'addq1', 'addq2', 'addq3', 'addq4', 'addq5', 'addq6', 'addq7', 'addq8']
  
  f_split=filename.split('.')[0].split()

  level = f_split[3][1:3]
  school_code = f_split[4].split('-')[0]
  course_code = f_split[4].split('-')[1]
  semester = f_split[6][:-1]
  year = f_split[7][:-1]

  df['year'] = int(year)
  df['semester'] = int(semester)
  df['level'] = level
  df['course_code'] = course_code

  df = df[['year', 'semester', 'level', 'course_code',
           'program_code', 'population', 'osi_count', 'gts_count', 'reliability',
           'gts', 'gts_mean', 'osi', 'osi_mean',
           'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6',
           'addq1', 'addq2', 'addq3', 'addq4', 'addq5', 'addq6', 'addq7', 'addq8'
           ]]

  df = df.infer_objects()
  
  df[['gts', 'gts_mean', 'osi', 'osi_mean',
      'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6',
      'addq1', 'addq2', 'addq3', 'addq4', 'addq5', 'addq6', 'addq7', 'addq8']] \
    = df[['gts', 'gts_mean', 'osi', 'osi_mean',
          'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6',
          'addq1', 'addq2', 'addq3', 'addq4', 'addq5', 'addq6', 'addq7', 'addq8']].apply(pd.to_numeric, errors='coerce')
  
  df = df.loc[df['osi_count'].notna()]

  try:
    df.to_sql(name=tbl_name,
              con=engine,
              schema=schema,
              if_exists='append',
              index=False
              )
  except:
    print(filename)
    print(df)
    
    pass


# get data from excel doc
# open template
directory = 'H:\\Data\\CoB Database\\CES\\Course_program\\'

for filename in os.listdir(directory):
    if filename.endswith(".xls") or filename.endswith(".py"):
        print(os.path.join(directory, filename))
        upload_course_prog_data_from_excel(directory, filename, postgres_engine)
        continue
    else:
        continue

