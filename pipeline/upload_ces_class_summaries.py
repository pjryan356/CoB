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
directory = 'H:\\Data\\CoB Database\\CES\\\class_teacher\\'


# Function to load:
#   - Course Offering data; and
#       - This will include Course Clusters and Vertical Studios
#   - Teacher Class data;
# into database
def upload_course_data_from_excel(directory, filename, engine,
                                  course_tbl_name='tbl_course_summaries',
                                  class_teacher_tbl_name='tbl_class_teacher_summaries',
                                  schema='ces'):
  
  # Load all data from filename
  # The first 4 rows are headers and hence are skipped
  # The last 5 rows are ignored (This is probably redundant)
  
  # Data includes two level of aggregation:
  #   - course objects; and
  #   - class teacher;
  
  # The All_flag in column 2 determines that the data is for the Course Object level
  #   - in most circumstances this is course offering level. Exceptions are Vertical Studios and Clusters
  #   - Vertical Studios and Clusters are 'fixed' in the database
  
  # The row will contain a class and term code (columns 3 and 4) if it is at Class teacher level
  
  # Note: A row can be at both course and class teacher level
  
  df = pd.read_excel(directory + filename,
                     sheet_name='Sheet1',
                     skiprows=4,
                     usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27],
                     skipfooter=5)
  
  df.columns = ['course_code_ces','all_flag', 'class_nbr', 'term_code', 'section_code', 'course_name',
                'teaching_staff', 'course_coordinator', 'career',
                'population', 'osi_count', 'gts_count', 'reliability', 'campus',
                'gts', 'gts_mean', 'osi', 'osi_mean',
                'international_count', 'domestic_count', 'ft_count', 'pt_count',
                'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']
  
  # Gather information (year, semester, level) from the filename
  f_split=filename.split('.')[0].split()
  
  level = f_split[4][1:3] # brackets removed
  semester = f_split[7][:-1] # comma removed
  year = f_split[8][:-1] # bracket removed
  
  df['year'] = int(year)
  df['semester'] = int(semester)
  df['level'] = level
  
  # Three types of Course Code are created:
  #   - course_code (The Course Offering Code that aligns with SAMS)
  #   - course_code_ces (The Course Code provided by the CES survey (SVnn and CLnn))
  #   - course_code_ces2 (The course Code provided by the CES survey with nn removed
  #     this is done so that vertical studios can be combined

  temp = df['course_code_ces'].str.split('-', n=1, expand=True)
  df['course_code'] = temp[0]
  df['course_code_ces2'] = temp[0] + '-' + temp[1].str[:2]
  df['course_code_ces2'] = df['course_code_ces2'].combine_first(df['course_code'])
  
  
  # Prepare data for course_level table
  # Get all data with All flag
  df_courses = df.loc[df['all_flag'] == 'All']

  # Limit to columns relevant to course (remove section, class, term, teacher)
  df_courses: object = df_courses[[
    'year', 'semester', 'level',
    'course_code', 'course_code_ces', 'course_code_ces2',
    'course_name',
    'course_coordinator', 'career', 'campus',
    'international_count', 'domestic_count', 'ft_count', 'pt_count',
    'population', 'reliability',
    'osi_count', 'osi', 'osi_mean',
    'gts_count', 'gts', 'gts_mean',
    'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6'
  ]]


  # Correct data types
  df_courses = df_courses.infer_objects()

  df_courses[['gts', 'gts_mean', 'osi', 'osi_mean',
              'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']] \
    = df_courses[['gts', 'gts_mean', 'osi', 'osi_mean',
                  'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']].apply(pd.to_numeric, errors='coerce')

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
    'year', 'semester', 'level',
    'course_code', 'course_code_ces', 'course_code_ces2',
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

