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


def upload_course_comments_from_excel(directory, filename, engine,
                                      tbl_name='tbl_course_comments',
                                      schema='ces_oua'):
  # Use file name for information
  fn_split = filename.split('_')
  year = fn_split[2]
  level = fn_split[3]
  if fn_split[4] == 'GC':
    period = fn_split[5]
  else:
    period = fn_split[4]
  
  # gets ces comments data the suuplied excel files and uploads them to postrgres
  ## gets the first sheet (sheet_name=0)
  df = pd.read_excel(directory + filename,
                     sheet_name=0,
                     skiprows=0,
                     usecols=[0, 1, 2, 3],
                     skipfooter=0)
  
  df.columns = ['classkey', 'course', 'best', 'improve'
                ]
  
  df['year'] = int(year)
  df['period'] = period
  df['level'] = level
  
  df: object = df[[
    'year', 'period',
    'level', 'classkey', 'course',
    'best', 'improve'
  ]]
  
  df = df.infer_objects()
  
  df = df.loc[df['classkey'].notna()]

  # print(tabulate(df, headers='keys'))
  
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


# get data from excel doc
# open template
directory = 'H:\\Data\\CoB Database\\CES\\OUA\\comments\\'

for filename in os.listdir(directory):
  if filename.endswith(".xlsx"):
    print(os.path.join(directory, filename))
    upload_course_comments_from_excel(directory, filename, postgres_engine)
    print(filename)
    continue
  else:
    continue

