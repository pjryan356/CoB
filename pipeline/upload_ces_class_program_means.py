'''
Load CES class summaries and class teacher data
  - from excel files downloaded from Survey Team google drive
  - into Local postgres Database
      - ces.tbl_course_program_post2018

First download VE & HE files from google drive into 'directory' and
if necessary update line 41 directory = ......
  - currently two separate file sets (PA and Mean) are received.
  - ensure that only PA files are in directory
  - there is a separate script to load the Mean files
  - ensure that the file format (columns etc.) has not changed before running this script
  - ensure that filename format has not changed

Peter Ryan December 2019
'''

import os
import pandas as pd
import numpy as np
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
directory = 'H:\\Data\\CoB Database\\CES\\Course_program\\Mean\\2020 S1\\Mean\\'

# Function to load:
#   - Course Program data; and
#       - This will include Course Clusters
# into database
def upload_course_prog_data_from_excel(directory, filename, engine, tbl_name='tbl_course_program_means',
                                       schema='ces'):
  # Load all data from filename
  # The first 4 rows are headers and hence are skipped
  
  # Data includes two levels of aggregation:
  #   - course program objects; and
  #   - course; (This is not used)
  
  # The final row will contain the course summary values
  
  # Do not gather program details information
  df = pd.read_excel(directory + filename,
                     sheet_name='Sheet1',
                     skiprows=4,
                     usecols=[0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
                     skipfooter=0)
  
  df.columns = ['program_code', 'population', 'osi_count', 'gts_count', 'reliability',
                'gts', 'mgts', 'osi', 'mosi',
                'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6',
                'addq1', 'addq2', 'addq3', 'addq4', 'addq5', 'addq6', 'addq7', 'addq8']
  
  # Gather information (year, semester, level and program) from the filename
  ## 2019 file names had a differnt format as they include distinguish between PA/Mean in the filename
  ## The files themselves also change to add OSI mean column (col 16)
  
  f_split = filename.split('.')[0].split()
  level = f_split[4][1:3] # remove brackets
  course_code = f_split[5].split('-')[1]
  
  # Check for CL or SV code at end of course_code
  try:
    course_code_ces = course_code + '-' + f_split[5].split('-')[2]
  except:
    course_code_ces = course_code
  semester = f_split[7][:-1] # remove comma
  year = f_split[8][:-1] # remove bracket
  
  df['year'] = int(year)
  df['semester'] = int(semester)
  df['level'] = level
  df['course_code'] = course_code
  df['course_code_ces'] = course_code_ces

  df = df.loc[df['population'].notnull()]
  
  df = df[['year', 'semester', 'level', 'course_code', 'course_code_ces',
           'program_code', 'population', 'osi_count', 'gts_count', 'reliability',
           'gts', 'mgts', 'osi', 'mosi',
           'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6',
           'addq1', 'addq2', 'addq3', 'addq4', 'addq5', 'addq6', 'addq7', 'addq8'
           ]]
  
  df = df.infer_objects()
  
  df[['gts', 'mgts', 'osi', 'mosi',
      'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6',
      'addq1', 'addq2', 'addq3', 'addq4', 'addq5', 'addq6', 'addq7', 'addq8']] \
    = df[['gts', 'mgts', 'osi', 'mosi',
          'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6',
          'addq1', 'addq2', 'addq3', 'addq4', 'addq5', 'addq6', 'addq7', 'addq8']].apply(pd.to_numeric, errors='coerce')
  
  df = df.loc[df['osi_count'].notna()]
  
  try:
    df.to_sql(name=tbl_name,
              con=engine,
              schema=schema,
              if_exists='append',
              index=False
              )
    print(filename)
  except:
    pass

for filename in os.listdir(directory):
  if filename.endswith(".xls") or filename.endswith(".py"):
    print(os.path.join(directory, filename))
    upload_course_prog_data_from_excel(directory, filename, postgres_engine)
    continue
  else:
    continue

