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


def upload_sim_ces_data_from_excel(directory, filename, engine,
                                      schema='sim_ces'):
  
  # gets ces comments data the suuplied excel files and uploads them to postrgres
  df = pd.read_excel(directory + filename,
                     sheet_name='Summary',
                     skiprows=1,
                     usecols=[0,1,2,3,4,8,9,10,11,12,13,14],
                     skipfooter=0)

  df.columns = ['subject', 'catalog', 'course_name', 'section_code', 'teaching_staff',
                'responses', 'population',
                'subject_content', 'lecturer_effectiveness', 'course_satisfaction',
                'comment_type', 'comment_text'
                ]
  
  df['year'] = int(2019)
  df['semester'] = int(1)
  
  df['course_code'] = df['subject'] + df['catalog'].map(str)
  
  df_ces: object = df[[
    'year', 'semester',
    'course_code', 'course_name', 'section_code', 'teaching_staff',
    'responses', 'population',
    'subject_content', 'lecturer_effectiveness', 'course_satisfaction'
  ]]
  
  df_ces = df_ces.drop_duplicates()
  #print(df_ces)
  
  try:
    df_ces .to_sql(
      name='tbl_course_teacher',
      con=engine,
      schema=schema,
      if_exists='append',
      index=False
      )
  except Exception as e:
    print('comment input failed' + filename)
    print(e)
    pass
  
  df_ces_com: object = df[[
    'year', 'semester',
    'course_code', 'course_name', 'section_code', 'teaching_staff',
    'comment_type', 'comment_text'
  ]]
  
  df_ces_com = df_ces_com[df_ces_com['comment_text'] != '-']
  df_ces_com = df_ces_com[df_ces_com['comment_text'] != 'nil']
  df_ces_com = df_ces_com[df_ces_com['comment_text'] != 'nil.']
  df_ces_com = df_ces_com[df_ces_com['comment_text'] != '-nil-']
  df_ces_com = df_ces_com[df_ces_com['comment_text'] != 'NIL']
  df_ces_com = df_ces_com[df_ces_com['comment_text'] != '-NIL-']
  df_ces_com = df_ces_com[df_ces_com['comment_text'] != 'Nil']
  df_ces_com = df_ces_com[df_ces_com['comment_text'] != 'NA']
  df_ces_com = df_ces_com[df_ces_com['comment_text'] != 'na']
  df_ces_com = df_ces_com[df_ces_com['comment_text'] != 'Na']
  df_ces_com = df_ces_com[df_ces_com.comment_text.notnull()]
  df_ces_com = df_ces_com[df_ces_com.comment_type.notnull()]
  df_ces_com = df_ces_com[df_ces_com['comment_type'] != '-']
  
  print (df_ces_com)
  
  '''
  try:
    df_ces_com.to_sql(
      name='tbl_course_teacher_comments',
      con=engine,
      schema=schema,
      if_exists='append',
      index=False
      )
  except Exception as e:
    print('comment input failed' + filename)
    print(e)
    pass
  '''
  
# get data from excel doc
# open template
directory = 'H:\\Data\\SIM\\'
filename = 'SIM CES Jan 2019.xlsx'


print(os.path.join(directory, filename))
upload_sim_ces_data_from_excel(directory, filename, postgres_engine)

