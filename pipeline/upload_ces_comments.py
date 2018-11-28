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
                                      schema='ces'):
  # gets ces comments data the suuplied excel files and uploads them to postrgres
  df = pd.read_excel(directory + filename,
                     sheet_name='BUS',
                     skiprows=2,
                     usecols=[0,1,2,3,4,5,6,7],
                     skipfooter=0)

  df.columns = ['school_code', 'classkey', 'course_name', 'career', 'program_code',
                'best', 'improve'
                ]
  
  year = input("Year: ")
  semester = input("Semester: ")
  
  df['year'] = int(year)
  df['semester'] = int(semester)

  df: object = df[[
    'year', 'semester',
    'school_code', 'classkey', 'course_name', 'career', 'program_code',
    'best', 'improve'
  ]]

  mask = df.program_code == 'Unknown'
  df.loc[mask, 'program_code'] = 'UNKNW'
  
  df = df.infer_objects()

  df = df.loc[df['classkey'].notna()]
  
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

  
# get data from excel doc
# open template
directory = 'H:\\Data\\CoB Database\\CES\\comments\\'

for filename in os.listdir(directory):
    if filename.endswith(".xlsx"):
        print(os.path.join(directory, filename))
        upload_course_comments_from_excel(directory, filename, postgres_engine)
        continue
    else:
        continue

