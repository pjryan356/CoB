## Load CES response rate data
# Data from excel doc place on Course and Student Survey
#   (https://www.rmit.edu.au/staff/teaching-supporting-students/course-and-student-surveys
# Place into local database

import os
import pandas as pd
import psycopg2
from sqlalchemy import (create_engine, orm)
from tabulate import tabulate
import datetime as dt

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


# Inputs
directory = 'H:\\Data\\CoB Database\\CES\\Response Rate\\2020\\' #input("Directory: ")
filename = 'Wk3 RRate20201009.xlsx' #input("Filename: ")
date_tbl_name = 'tbl_class_responses'
input_date = dt.date(2020,10,9)

def load_ces_response_rate(date, directory, filename, schema='ces_responses', date_tbl_name='tbl_class_responses'):
  
  for sector in ['HE', 'VE']:
    # get data from excel docprint(tabulate(df, headers='keys'))
    df = pd.read_excel(directory + filename,
                       sheet_name=sector,
                       skiprows=3,
                       usecols=[0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                       skipfooter=1)

    df.columns = ['classkey', 'level', 'college', 'school_code',
                  'session_code', 'section_code', 'survey_start_date', 'survey_end_date',
                  'campus', 'invitations', 'responses']
  
    df = df.infer_objects()

    df[['invitations', 'responses']] \
      = df[['invitations', 'responses']].apply(pd.to_numeric, errors='coerce')


    df['date'] = date
    
    df = df[['level', 'date', 'classkey', 'college', 'school_code',
             'survey_start_date', 'survey_end_date',
             'campus', 'invitations', 'responses']]
    
    df = df.loc[df['level'] == sector]
    print(tabulate(df, headers='keys'))
    
    df.to_sql(name='{}'.format(date_tbl_name),
              con=postgres_engine,
              schema=schema,
              if_exists='append',
              index=False
              )


load_ces_response_rate(input_date, directory, filename, 'ces_responses')
