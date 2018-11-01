## EXAMPLES OF USING SAMS HELPER FUNCTIONS
# For Peter August 2018
# Demonstrates the use of the three different connection types
# PUT THE PASSWORD STRING IN

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


# Get inputs
password_str = input("SAMS Password: ")
st_term = input("Update from Start term: ")
end_term = input("Update until End term: ")
postgres_pw = input("Postgres Password: ")

# Create connections
# create sams engine this is the connection to the oracle database
sams_engine = return_sams_engine(password_str=password_str)

# create postgres engine this is the connection to the oracle database
postgres_user = 'pjryan'
postgres_host = 'localhost'
postgres_dbname = 'postgres'

engine_string = 'postgresql+psycopg2://{}:{}@{}/{}'.format(postgres_user,
                                                           postgres_pw,
                                                           postgres_host,
                                                           postgres_dbname)
postgres_engine = create_engine(engine_string)
postgres_con = postgres_engine.connect()

# get data from sams
sams_qry = qry_std_class_grades(st_term=st_term, end_term=end_term)

try:
  df = pd.read_sql(sql=sams_qry, con=sams_engine)
except:
  print(sams_qry)

print(len(df))


# Add update statement to table description
date = dt.datetime.now().date()
qry_comment = """
COMMENT ON TABLE enrolments.tbl_std_class_enrl_grades_raw
    IS 'Updated on {0} for {1} to {2}'
;
""".format(date.strftime('%d-%m-%Y'), st_term, end_term)

print(qry_comment)
trans = postgres_con.begin()
postgres_con.execute(qry_comment)
trans.commit()