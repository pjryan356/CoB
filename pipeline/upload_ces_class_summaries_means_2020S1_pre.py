'''
Load CES class summaries and class teacher data
  - from excel files downloaded from Survey Team google drive
  - into Local postgres Database
      - ces.tbl_course_summaries
      - ces.tbl_class_teacher_summaries

First download VE & HE files from google drive into 'directory' and update below
  - currently two separate file sets (PA and Mean) are received.
  - ensure that only Mean files are in directory
  - there is a separate script to load the PA files
  - ensure that the file format has not changed before running this script
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
directory = 'H:\\Projects\\CoB\\CES\\Data\\Prelim 2020 S1\\'

# Function to load:
#   - Course Offering data; and
#       - This will include Course Clusters and Vertical Studios
#   - Teacher Class data;
# into database

def upload_course_data_from_excel(directory, filename, engine,
                                  course_tbl_name='tbl_course_summaries_means',
                                  schema='ces'):
  # gets course ces data split by program from the suuplied excel files and uploads them to postrgres
  df = pd.read_excel(directory + filename,
                     sheet_name='Sheet1',
                     skiprows=4,
                     usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28],
                     skipfooter=5)

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
  
  df.columns = ['course_code_ces','all_flag', 'class_nbr', 'term_code', 'school_code', 'section_code', 'course_name',
                'teaching_staff', 'course_coordinator', 'career',
                'population', 'osi_count', 'gts_count', 'reliability', 'campus',
                'gts', 'mgts', 'osi', 'mosi',
                'int_count', 'dom_count', 'ft_count', 'pt_count',
                'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']


  # Gather information (year, semester, level) from the filename
  f_split=filename.split('.')[0].split()
  
  level = 'VE' # brackets removed
  semester = 1 # comma removed
  year = 2020 # bracket removed
  
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
    'year', 'semester', 'level', 'school_code',
    'course_code', 'course_code_ces', 'course_code_ces2',
    'course_name',
    'course_coordinator', 'career', 'campus',
    'int_count', 'dom_count', 'ft_count', 'pt_count',
    'population', 'reliability',
    'osi_count', 'osi', 'mosi',
    'gts_count', 'gts', 'mgts',
    'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6'
  ]]

  # Correct data types
  df_courses = df_courses.infer_objects()

  df_courses[['gts', 'mgts', 'osi', 'mosi',
              'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']] \
    = df_courses[['gts', 'mgts', 'osi', 'mosi',
                  'mgts1', 'mgts2', 'mgts3', 'mgts4', 'mgts5', 'mgts6']].apply(pd.to_numeric, errors='coerce')

  print(tabulate(df_courses, headers='keys'))
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
  



# Iterate through files in directory
for filename in os.listdir(directory):
    if filename.endswith(".xls"):
        print(os.path.join(directory, filename))
        upload_course_data_from_excel(directory, filename, postgres_engine)
        continue
    else:
        continue

