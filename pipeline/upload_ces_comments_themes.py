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

directory = 'C:\\Users\\e35137\\Downloads\\'
filename = 'Comment_themes_2018S2_Wave3_VBE_S1_leftovers.xlsx'

def upload_course_comments_themes_from_excel(directory, filename, engine,
                                      tbl_name='tbl_course_thematic',
                                      schema='course_enhancement'):
  # gets ces comments data the suuplied excel files and uploads them to postrgres
  df = pd.read_excel(directory + filename,
                     sheet_name='Sheet1',
                     skiprows=0,
                     usecols=[0,1,2,3,4],
                     skipfooter=0)

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

  
# get data from excel doc
# open template
directory = 'C:\\Users\\e35137\\Downloads\\'
filename = 'Comment_themes_2018S2_Wave3_VBE_S1_leftovers.xlsx'

print(os.path.join(directory, filename))
upload_course_comments_themes_from_excel(directory, filename, postgres_engine)


