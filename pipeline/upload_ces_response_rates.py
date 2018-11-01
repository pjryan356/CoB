## Load CES response rate data
# Data from excel doc place on Course and Student Survey
#   (https://www.rmit.edu.au/staff/teaching-supporting-students/course-and-student-surveys
# Place into local database

from sams_helper_functions import *
import pandas as pd
import tabulate
from sams_queries import *
from postgres_queries import (qry_create_table_course_location,
                              qry_add_comment,
                              qry_drop_table,
                              qry_delete_after_term)
import datetime as dt
import psycopg2
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


# get data from excel doc
# open template
directory = 'c:\\Peter\\'
#import openpyxl
filename = 'RRate20181023.xlsx'
#wb = openpyxl.load_workbook(directory + filename)
#sheet = wb['sheet1']

df = pd.read_excel(directory + filename,
                   sheet_name='HE',
                   skiprows=3,
                   usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13],
                   skipfooter=1)

df.columns = ['classkey', 'level', 'course_name', 'college', 'school_code',
              'session_code', 'section_code', 'survey_start_date', 'survey_end_date',
              'campus', 'invitations', 'responses', 'response_rate']


#year = input("Year: ")
#level = input("Semester: ")
#date = input("Date: ")

#df['year'] = int(year)
#df['semester'] = int(semester)
#df['level'] = level


df = df.infer_objects()

#print(df)
#print(df.iloc[0])
#print(df.iloc[-1])


df[['invitations', 'responses', 'response_rate']] \
  = df[['invitations', 'responses', 'response_rate']].apply(pd.to_numeric, errors='coerce')


df.to_sql(name='he_20181023',
            con=postgres_engine,
            schema='ces_responses',
            if_exists='append',
            index=False
          )

df = pd.read_excel(directory + filename,
                   sheet_name='VE',
                   skiprows=3,
                   usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13],
                   skipfooter=1)

df.columns = ['classkey', 'level', 'course_name', 'college', 'school_code',
              'session_code', 'section_code', 'survey_start_date', 'survey_end_date',
              'campus', 'invitations', 'responses', 'response_rate']


#year = input("Year: ")
#level = input("Semester: ")
#date = input("Date: ")

#df['year'] = int(year)
#df['semester'] = int(semester)
#df['level'] = level


df = df.infer_objects()

#print(df)
#print(df.iloc[0])
#print(df.iloc[-1])

df[['invitations', 'responses', 'response_rate']] \
  = df[['invitations', 'responses', 'response_rate']].apply(pd.to_numeric, errors='coerce')

df.to_sql(name='ve_20181023',
            con=postgres_engine,
            schema='ces_responses',
            if_exists='append',
            index=False
          )


