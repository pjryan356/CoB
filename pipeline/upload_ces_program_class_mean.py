'''
Load CES program class summaries and program summaries data
  - from excel files downloaded from Survey Team google drive
  - into Local postgres Database
      - ces.tbl_program_class_post2018
      - ces.tbl_program_post2018

First download from google drive into 'directory' and
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
directory = 'H:\\Data\\CoB Database\\CES\\Program_course\\Mean\\'


# Function to load:
#   - Program Class data; and
#       - This will include Course Clusters and Vertical Studios
#   - Program data;
# into database
def upload_program_course_data_from_excel(directory, filename, engine,
                                  program_course_tbl_name='tbl_program_class_means',
                                  program_tbl_name='tbl_program_means',
                                  schema='ces'):
  # Load all data from filename
  # The first 4 rows are headers and hence are skipped
  
  # Data includes two level of aggregation:
  #   - course objects; and
  #   - class teacher;
  
  # The All_flag in column 2 determines that the data is for the Course Object level
  #   - in most circumstances this is course offering level. Exceptions are Vertical Studios and Clusters
  #   - Vertical Studios and Clusters are 'fixed' in the database
  #   - This data is ignored as it has already been capture by class summaries files
  #     - with the excpetion of courses outside the CoB (these are still ignored)
  
  # The all_flag (Column 4) will contain the program code if it is at the program course level
  
  # The final row will contain the program summary values

  # Gather information (year, semester, level and program) from the filename
  ## 2019 file names had a differnt format as they include distinguish between PA/Mean in the filename
  ## The files themselves also change to add OSI mean column (col 16)
  
  f_split = filename.split('.')[0].split()
  level = f_split[4][1:3]  # brackets removed
  semester = int(f_split[7][:-1])  # comma removed
  year = int(f_split[8][:-1])  # bracket removed
  program_code = f_split[5].split('-')[1]  # remove school_code
  
  # column order for pre 2019

  # course and program detail information is removed (1,3,4,5,7,12)
  df = pd.read_excel(directory + filename,
                     sheet_name='Sheet1',
                     skiprows=4,
                     usecols=[0, 2, 4, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
                     skipfooter=13)

  df.columns = ['course_code_ces', 'class_nbr',
                'all_flag',
                'population', 'osi_count', 'gts_count', 'reliability',
                'gts', 'mgts', 'osi', 'mosi',
                'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']
  
  # Input values from filename
  df['year'] = int(year)
  df['semester'] = int(semester)
  df['level'] = level
  df['program_code'] = program_code
  
  
  # Prepare data for program_course_level table
  # Remove rows where all_flag ='All' (This is whole class data already loaded from class summary files
  df_prg_courses = df.loc[df['all_flag'] != 'All']
  df_prg_courses = df_prg_courses.loc[df['all_flag'].notnull()]

  # Remove all flag column
  df_prg_courses: object = df_prg_courses[[
    'year', 'semester', 'level', 'program_code',
    'course_code_ces', 'class_nbr',
    'population', 'osi_count', 'gts_count', 'reliability',
    'gts', 'mgts', 'osi', 'mosi',
    'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6'
  ]]

  # Correct data types
  df_prg_courses = df_prg_courses.infer_objects()

  df_prg_courses[['mgts', 'mgts', 'osi', 'mosi',
              'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']] \
    = df_prg_courses[['gts', 'mgts', 'osi', 'mosi',
                  'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']].apply(pd.to_numeric, errors='coerce')

  df_prg_courses.class_nbr = df_prg_courses.class_nbr.astype(np.int64)

  df_prg_courses['class_nbr'].apply(str)

  # Load into database
  try:
    df_prg_courses.to_sql(
      name=program_course_tbl_name,
      con=engine,
      schema=schema,
      if_exists='append',
      index=False
      )
  except Exception as e:
    print(e)
    print('course input failed' + filename)
    pass
  
  # Prepare data for Porgram level table
  # Get all data without a class number & Program code in first column
  
  df_program = df.loc[(df['course_code_ces'].str.contains(program_code)) & df['class_nbr'].isnull()]
  
  # Remove unnecessary columns
  df_program: object = df_program[[
    'year', 'semester', 'level',
    'program_code',
    'population', 'osi_count', 'gts_count', 'reliability',
    'gts', 'mgts', 'osi', 'mosi',
    'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6'
  ]]


  # Correct data types
  df_program = df_program.infer_objects()

  df_program[['gts', 'mgts', 'osi', 'mosi',
              'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']] \
    = df_program[['gts', 'mgts', 'osi', 'mosi',
                  'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']].apply(pd.to_numeric, errors='coerce')

  # Load into database
  try:
    df_program.to_sql(
      name=program_tbl_name,
      con=engine,
      schema=schema,
      if_exists='append',
      index=False
      )
  except Exception as e:
    print(e)
    print('program input failed' + filename)
    pass


for filename in os.listdir(directory):
    if filename.endswith(".xls"):
        print(os.path.join(directory, filename))
        upload_program_course_data_from_excel(directory, filename, postgres_engine)
        continue
    else:
        continue

