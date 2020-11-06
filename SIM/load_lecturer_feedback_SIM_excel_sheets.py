## Saves excel sheets into seperate files
# Peter Ryan May 2019

import os
import xlrd
from xlutils.copy import copy
import xlwt
import pandas as pd
from tabulate import tabulate
from sqlalchemy import (create_engine, orm)

year = 2019
semester = 1
file_string_check = '(RMIT copy)'
#

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

def load_lecture_feedback_to_db(path, filename, engine):
  # Load workbook
  try:
    wb = xlrd.open_workbook(os.path.join(path, filename), on_demand=True)
  except:
    print(path + filename + ' failure')
    return
  
  #iterate through sheets
  for sheet in wb.sheets():
    
    # Iterate through columns to account for multiple responses
    i_col = 0
    while True:
      i_col += 1
      
      # Load sheet into pd
      df = pd.read_excel(path + filename,
                         sheet_name=sheet.name,
                         skiprows=0,
                         usecols=[0, i_col],
                         skipfooter=0)

      # break if column is empty
      try:
        df.columns = ['question', 'answer']
      except:
        print('{}: Last Column: {}'.format(sheet.name, i_col))
        break
      
      # Add additional columns
      df['year'] = year
      df['semester'] = semester
      df['course_code'] = sheet.name
      df['comment'] = ''
      
      # Reorder columns
      df: object = df[[
        'year', 'semester',
        'course_code', 'question', 'answer', 'comment'
      ]]
      
      # Combine answer and comment into single row
      i = 0
      while i <= 10:
        df.iloc[i, 5] = df.iloc[i+1, 4]
        i += 2
      
      # Move final comment into comment column
      df.iloc[i, 5] = df.iloc[i, 4]
      df.iloc[i, 4] = ''
      
      # Filter columns to relevant rows
      df1 = df.loc[df['question'] != 'Comments']

      try:
        df1.to_sql(
          name='tbl_lecture_feedback',
          con=engine,
          schema='sim_ces',
          if_exists='append',
          index=False
          )
      except Exception as e:
        print('comment input failed' + filename)
        print(e)
        pass


for school in ['Accountancy', 'Econ & Fin', 'Logistics', 'Management & Int Bus', 'Marketing']:
  path = 'H:\\Data\\SIM\\{0}\\{1}S{2}\\'.format(school, year, semester)
  
  for root, dir, files in os.walk(path, topdown=False):
    for file in files:
      if file_string_check in file:
        print(file)
        load_lecture_feedback_to_db(root, file, postgres_engine)

