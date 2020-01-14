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



directory = 'H:\\Data\\CoB Database\\'
filename = 'Book1.xlsx'

# get data xlsx
clo_df = pd.read_excel(open(directory+filename, 'rb'), converters={'crse_id': str})


print(tabulate(clo_df, headers='keys'))

clo_df.to_sql(name='tbl_course_det_20191018',
            con=postgres_engine,
            schema='lookups',
            if_exists='append',
            index=False
          )



