## Load CES course_program data excel files downloaded from Survey Team google drive
# Peter Ryan October 2018

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


def upload_course_data_from_excel(directory, filename, engine,
                                  course_tbl_name='tbl_course_summaries',
                                  class_teacher_tbl_name='tbl_class_teacher_summaries',
                                  schema='ces'):
  # gets course ces data split by program from the suuplied excel files and uploads them to postrgres
  df = pd.read_excel(directory + filename,
                     sheet_name='Sheet1',
                     skiprows=4,
                     usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27],
                     skipfooter=5)
  #print(tabulate(df, headers='keys'))
  df.columns = ['course_code_ces','all_flag', 'class_nbr', 'term_code', 'section_code', 'course_name',
                'teaching_staff', 'course_coordinator', 'career',
                'population', 'osi_count', 'gts_count', 'reliability', 'campus',
                'gts', 'gts_mean', 'osi', 'osi_mean',
                'international_count', 'domestic_count', 'ft_count', 'pt_count',
                'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']
  #print(tabulate(df, headers='keys'))
  f_split=filename.split('.')[0].split()

  level = f_split[3][1:3] # brackets removed
  semester = f_split[6][:-1] # comma removed
  year = f_split[7][:-1] # bracket removed
  
  df['year'] = int(year)
  df['semester'] = int(semester)
  df['level'] = level
  
  # create alternate course_codes
  temp = df['course_code_ces'].str.split('-', n=1, expand=True)
  df['course_code'] = temp[0]
  df['course_code_ces2'] = temp[0] + '-' + temp[1].str[:2]
  df['course_code_ces2'] = df['course_code_ces2'].combine_first(df['course_code'])
  df['cluster_code'] = temp[1]
  
  
  # prepare data for course_level table
  df_courses = df.loc[df['all_flag'] == 'All']

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

  df_courses = df_courses.infer_objects()

  df_courses[['gts', 'gts_mean', 'osi', 'osi_mean',
              'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']] \
    = df_courses[['gts', 'gts_mean', 'osi', 'osi_mean',
                  'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']].apply(pd.to_numeric, errors='coerce')

  #print(tabulate(df_courses, headers='keys'))
  #print(int('df'))

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

  # prepare data for teacher_course_level table
  df_teacher = df.loc[df['class_nbr'].notnull()]

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

  df_teacher = df_teacher.infer_objects()

  df_teacher[['gts', 'gts_mean',
              'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']] \
    = df_teacher[['gts', 'gts_mean',
                  'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']].apply(pd.to_numeric, errors='coerce')

  df_teacher.term_code = df_teacher.term_code.astype(np.int64)
  df_teacher.class_nbr = df_teacher.class_nbr.astype(np.int64)
  
  df_teacher['class_nbr'].apply(str)
  df_teacher['term_code'].apply(str)
  
  #print(tabulate(df_teacher, headers='keys'))
  #int('df')
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
  
  print(df_teacher.iloc[-1])
  
  
# get data from excel doc
# open template
directory = 'H:\\Data\\CoB Database\\CES\\\class_teacher\\'
directory = 'C:\\Peter\\CoB\\'

for filename in os.listdir(directory):
    if filename.endswith(".xls"):
        print(os.path.join(directory, filename))
        upload_course_data_from_excel(directory, filename, postgres_engine)
        continue
    else:
        continue

