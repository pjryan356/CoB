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


def upload_program_course_data_from_excel(directory, filename, engine,
                                  program_course_tbl_name='tbl_program_class_post2018',
                                  program_tbl_name='tbl_program_post2018',
                                  schema='ces'):
  # gets course ces data split by program from the suuplied excel files and uploads them to postrgres
  f_split = filename.split('.')[0].split()
  level = f_split[3][1:3] # brackets removed
  semester = int(f_split[6][:-1]) # comma removed
  year = int(f_split[7][:-1]) # bracket removed
  program_code = f_split[4].split('-')[1] # remove school_code
  
  
  if year < 2018:
    df = pd.read_excel(directory + filename,
                       sheet_name='Sheet1',
                       skiprows=4,
                       usecols=[0, 2, 4, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21],
                       skipfooter=10)
  
    df.columns = ['course_code_ces', 'class_nbr',
                  'all_flag',
                  'population', 'osi_count', 'gts_count', 'reliability',
                  'gts', 'gts_mean', 'osi',
                  'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']
    df['osi_mean'] = None
    
  else:
    df = pd.read_excel(directory + filename,
                       sheet_name='Sheet1',
                       skiprows=4,
                       usecols=[0, 2, 4, 8,9,10,11, 13,14,15,16, 17,18,19,20,21,22],
                       skipfooter=13)
  
    df.columns = ['course_code_ces', 'class_nbr',
                  'all_flag',
                  'population', 'osi_count', 'gts_count', 'reliability',
                  'gts', 'gts_mean', 'osi', 'osi_mean',
                  'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']
  
  df['year'] = int(year)
  df['semester'] = int(semester)
  df['level'] = level
  df['program_code'] = program_code
  
  # prepare data for program_course_level table
  df_courses = df.loc[df['all_flag'] != 'All']
  df_courses = df_courses.loc[df['all_flag'].notnull()]
  
  df_courses: object = df_courses[[
    'year', 'semester', 'level', 'program_code',
    'course_code_ces', 'class_nbr',
    'population', 'osi_count', 'gts_count', 'reliability',
    'gts', 'gts_mean', 'osi', 'osi_mean',
    'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6'
  ]]

  df_courses = df_courses.infer_objects()

  df_courses[['gts', 'gts_mean', 'osi', 'osi_mean',
              'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']] \
    = df_courses[['gts', 'gts_mean', 'osi', 'osi_mean',
                  'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']].apply(pd.to_numeric, errors='coerce')

  df_courses.class_nbr = df_courses.class_nbr.astype(np.int64)

  df_courses['class_nbr'].apply(str)
  
  try:
    int('df')
    df_courses.to_sql(
      name=program_course_tbl_name,
      con=engine,
      schema=schema,
      if_exists='append',
      index=False
      )
  except Exception as e:
    #print(e)
    #print('course input failed' + filename)
    pass
  
  # prepare data for teacher_course_level table
  df_program = df.loc[df['osi_count'].notnull()]
  print(tabulate(df_program, headers='keys'))
  df_program = df_program.loc[(df_program['course_code_ces'].str.contains(program_code)) & df_program['class_nbr'].isnull()]
  print(tabulate(df_program, headers='keys'))

  df_program: object = df_program[[
    'year', 'semester', 'level',
    'program_code',
    'population', 'osi_count', 'gts_count', 'reliability',
    'gts', 'gts_mean', 'osi', 'osi_mean',
    'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6'
  ]]

  df_program = df_program.infer_objects()

  df_program[['gts', 'gts_mean',
              'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']] \
    = df_program[['gts', 'gts_mean',
                  'gts1', 'gts2', 'gts3', 'gts4', 'gts5', 'gts6']].apply(pd.to_numeric, errors='coerce')

  print(tabulate(df_program, headers='keys'))
  
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

# get data from excel doc
# open template
directory = 'H:\\Data\\CoB Database\\CES\\Program_course\\'

for filename in os.listdir(directory):
    if filename.endswith(".xls"):
        print(os.path.join(directory, filename))
        upload_program_course_data_from_excel(directory, filename, postgres_engine)
        continue
    else:
        continue

