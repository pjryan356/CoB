## Load CES response rate data
# Data from excel doc place on Course and Student Survey
#   (https://www.rmit.edu.au/staff/teaching-supporting-students/course-and-student-surveys
# Place into local database

import os
import pandas as pd
import psycopg2
from sqlalchemy import (create_engine, orm)
from tabulate import tabulate


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
directory = input("Directory: ")
filename = input("Filename: ")


directory = 'C:\\Peter\\junk\\'
filename = 'course_enhancement_2019_s2_extra_2.csv'

# get data csv
df = pd.read_csv(directory + filename)


df = df.infer_objects()

print(tabulate(df, headers='keys'))


df.to_sql(name='tbl_courses',
            con=postgres_engine,
            schema='course_enhancement',
            if_exists='append',
            index=False
          )



