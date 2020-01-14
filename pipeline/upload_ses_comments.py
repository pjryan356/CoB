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


def upload_ses_comments_from_excel(directory, filename, engine,
                                      tbl_name='tbl_comments',
                                      schema='ses'):
  # gets ces comments data the suuplied excel files and uploads them to postrgres
  df = pd.read_excel(directory + filename,
                     skiprows=4,
                     usecols=[0, 1],
                     skipfooter=0)

  filename1 = filename.split(' - ')[0]
  filename2 = filename.split(' - ')[1]
  
  level = filename1.split('_')[1]
  program_code = filename1.split('_')[3]
  school_code = filename2.split('_')[2]
  year = filename2.split('_')[3].split('.')[0]
  
  df.columns = ['best', 'improve']
  df = df.dropna(subset=['best', 'improve'], how='all')
  df = df.fillna('')

  df['year'] = int(year)
  df['level'] = level
  df['school_code'] = school_code
  df['program_code'] = program_code

  df: object = df[[
    'year', 'level',
    'school_code', 'program_code',
    'best', 'improve'
  ]]
  
  df = df.infer_objects()
  
  #print(tabulate(df, headers='keys'))
  try:
    df.to_sql(
      name=tbl_name,
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
directory = 'H:\\Data\\CoB Database\\SES\\2018 SES HE Onshore\\'

for filename in os.listdir(directory):
    if filename.endswith(".xls"):
        print(os.path.join(directory, filename))
        upload_ses_comments_from_excel(directory, filename, postgres_engine)
        continue
    else:
        continue
'''

def upload_comments_from_excel(directory, filename, engine,
                               tbl_name='tbl_comments',
                               schema='public'):
  # gets ces comments data the suuplied excel files and uploads them to postrgres
  df = pd.read_excel(directory + filename,
                     skiprows=0,
                     skipfooter=0)

  print(tabulate(df, headers='keys'))
  
  df = df.dropna(subset=['best', 'improve'], how='all')
  df = df.fillna('')
  
  df = df.infer_objects()

  print(tabulate(df, headers='keys'))
  
  try:
    df.to_sql(
      name=tbl_name,
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
directory = 'H:\\Data\\CoB Database\\'

for filename in os.listdir(directory):
  if filename.endswith("Data 20191205.xlsx"):
    print(os.path.join(directory, filename))
    upload_comments_from_excel(directory, filename, postgres_engine)
    continue
  else:
    continue
'''