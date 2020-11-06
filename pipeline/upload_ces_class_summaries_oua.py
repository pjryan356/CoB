'''
Load CES class summaries and class teacher data
  - from excel files downloaded from Survey Team google drive
  - into Local postgres Database
      - ces.tbl_course_summaries
      - ces.tbl_class_teacher_summaries

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
directory = 'H:\\Data\\CoB Database\\OUA\\Summaries\\'


# Function to load:
#   - Course Offering data; and
#       - This will include Course Clusters and Vertical Studios
#   - Teacher Class data;
# into database
def upload_course_data_from_excel(directory, filename, engine,
                                  course_tbl_name='tbl_course_summaries',
                                  class_teacher_tbl_name='tbl_class_teacher_summaries',
                                  schema='ces_oua'):
  
  # Load all data from filename
  # The first 4 rows are headers and hence are skipped
  
  # Data includes two level of aggregation:
  #   - course objects; and
  #   - class teacher;
  
  # The All_flag in column 2 determines that the data is for the Course Object level
  
  # The row will contain a class and term code (columns 3 and 4) if it is at Class teacher level
  
  # Note: A row can be at both course and class teacher level
  
  df = pd.read_excel(directory + filename,
                     sheet_name='Sheet1',
                     skiprows=5,
                     usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31])
  
  df.columns = ['course_code','all_flag', 'class_nbr', 'term_code', 'section_code', 'course_name',
                'teaching_staff', 'course_coordinator', 'career',
                'population', 'osi_count', 'gts_count', 'reliability', 'campus',
                'gts', 'gts_mean', 'osi', 'osi_mean',
                'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6',
                'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8']
  
  # Gather information (year, semester, level) from the filename
  f_split=filename.split('.')[0].split('_')
  
  level = f_split[3]
  period = f_split[4]
  year = f_split[2]
  
  df['year'] = int(year)
  df['period'] = period
  df['level'] = level
  
  
  # Prepare data for course_level table
  # Get all data with All flag
  df_courses = df.loc[df['all_flag'] == 'All']

  # Limit to columns relevant to course (remove section, class, term, teacher)
  df_courses: object = df_courses[[
    'year', 'period', 'level',
    'course_code',
    'course_name',
    'course_coordinator', 'career', 'campus',
    'population', 'reliability',
    'osi_count', 'osi', 'osi_mean',
    'gts_count', 'gts', 'gts_mean',
    'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6',
    'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8'
  ]]


  # Correct data types
  df_courses = df_courses.infer_objects()

  df_courses[['gts', 'gts_mean', 'osi', 'osi_mean',
              'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6',
              'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8']] \
    = df_courses[['gts', 'gts_mean', 'osi', 'osi_mean',
                  'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6',
                  'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8']].apply(pd.to_numeric, errors='coerce')

  # Load into database
  try:
    df_courses.to_sql(
      name=course_tbl_name,
      con=engine,
      schema=schema,
      if_exists='append',
      index=False
      )
  except Exception as e:
    print('course input failed' + filename)
    pass

  # Prepare data for class teacher table
  # Get all data with a class number
  
  df_teacher = df.loc[df['class_nbr'].notnull()]

  # Limit to columns relevant to teacher (GTS only)
  df_teacher: object = df_teacher[[
    'year', 'period', 'level',
    'course_code',
    'class_nbr', 'term_code', 'section_code',
    'course_name',
    'teaching_staff',
    'course_coordinator', 'career', 'campus',
    'gts_count', 'gts', 'gts_mean',
    'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6'
  ]]

  # Correct Data types
  df_teacher = df_teacher.infer_objects()

  df_teacher[['gts', 'gts_mean',
              'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']] \
    = df_teacher[['gts', 'gts_mean',
                  'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']].apply(pd.to_numeric, errors='coerce')

  df_teacher.term_code = df_teacher.term_code.astype(np.int64)
  df_teacher.class_nbr = df_teacher.class_nbr.astype(np.int64)
  
  df_teacher['class_nbr'].apply(str)
  df_teacher['term_code'].apply(str)

  # Load into database
  try:
    df_teacher.to_sql(
      name=class_teacher_tbl_name,
      con=engine,
      schema=schema,
      if_exists='append',
      index=False
      )
  except Exception as e:
    print('teacher input failed' + filename)
    pass
  
  # Print last teacher loaded to check against bottom row
  print(df_teacher.iloc[-1])
  

# Iterate through files in directory
for filename in os.listdir(directory):
    if filename.endswith(".xls"):
        print(os.path.join(directory, filename))
        upload_course_data_from_excel(directory, filename, postgres_engine)
        continue
    else:
        continue

