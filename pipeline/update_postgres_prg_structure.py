## Update script to upload program detials table in local db
# Peter Ryan 2019 Feb

import datetime as dt
import psycopg2
from sqlalchemy import (create_engine, orm, String)
import pandas as pd
from tabulate import tabulate

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
sams_qry = qry_program_course_structure(program_code=None, active=False)

try:
  df = pd.read_sql(sql=sams_qry, con=sams_engine)
except:
  print(sams_qry)


x = postgres_con.execute(qry_delete_after_term(schema='programs',
                                               table='tbl_plan_course_structure',
                                               term_code=None),
                         )


df.to_sql(name='tbl_plan_course_structure',
          con=postgres_engine,
          schema='programs',
          if_exists='append',
          index=False,
          dtype={"program_code": String(), "plan_code": String()}
          )

# Add update statement to table description
date = dt.datetime.now().date()
qry_comment = """
COMMENT ON TABLE {1}.{2}
    IS 'Updated on {0}'
;
""".format(date.strftime('%d-%m-%Y'), 'programs', 'tbl_plan_course_structure')

print(qry_comment)
trans = postgres_con.begin()
postgres_con.execute(qry_comment)
trans.commit()



