## Update script to upload program detials table in local db
# Peter Ryan Nov 2018

import datetime as dt
import psycopg2
from sqlalchemy import (create_engine, orm)
import pandas as pd
import tabulate

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc
from general.sams_queries import *
from general.sams_helper_functions import *
from general.postgres_queries import (
  qry_delete_after_term)

# Get inputs
password_str = input("SAMS Password: ")

# Create connections
# create sams engine this is the connection to the oracle database
sams_engine = return_sams_engine(password_str=password_str)

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


# get data from sams
sams_qry = qry_program_details()
print(sams_qry)
int('f')
try:
  df = pd.read_sql(sql=sams_qry, con=sams_engine)
except:
  print(sams_qry)

print(len(df))

x = postgres_con.execute(qry_delete_after_term(schema='lookups',
                                               table='tbl_program_details',
                                               term_code=None),
                         )

#print(tabulate.tabulate(result_dataframe.iloc[:10], headers='keys'))

df.to_sql(name='tbl_program_details',
          con=postgres_engine,
          schema='lookups',
          if_exists='append',
          index=False
          )

print(tabulate.tabulate(df.iloc[:10], headers='keys'))

# Add update statement to table description
date = dt.datetime.now().date()
qry_comment = """
COMMENT ON TABLE lookups.tbl_program_details
    IS 'Updated on {0}'
;
""".format(date.strftime('%d-%m-%Y'))

print(qry_comment)
trans = postgres_con.begin()
postgres_con.execute(qry_comment)
trans.commit()



