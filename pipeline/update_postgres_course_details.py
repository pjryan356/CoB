## Update script to upload course details table in local db
# Peter Ryan Mar 2020

import datetime as dt
from sqlalchemy import (create_engine)
import pandas as pd

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

from general.sams_queries import *
from general.sams_helper_functions import *
from general.postgres_queries import (
  qry_delete_after_term)

# Get inputs
password_str = input("SAMS Password: ")
postgres_pw = input("Postgres Password: ")
st_term = input("Update from Start term: ")
end_term = input("Update until End term: ")

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

def qry_course_details(st_term='1700', end_term='1900'):
  qry = '''
SELECT
  	course_id,
	course_code,
	course_name,
	term_code,
	acad_career,
	school_code,
	college,
	campus,
	LISTAGG(instruction_mode, '; ') WITHIN GROUP (ORDER BY instruction_mode) AS instruction_modes
FROM (
	SELECT DISTINCT
  	cl.crse_id AS course_ID,
	cl.subject||cl.catalog_nbr AS course_code,
	cl.descr AS course_name,
	cl.strm AS term_code,
	cl.acad_career,
	cl.acad_org AS school_code,
	CASE
	  WHEN cl.acad_group = 'SET' THEN 'SEH'
	  WHEN cl.acad_group = 'BUS' THEN 'CoBL'
		ELSE cl.acad_group END AS college,
	cl.campus,
	instruction_mode

	FROM ps_class_tbl cl
	WHERE strm > '1700' AND strm <= '2100'
		AND enrl_tot > 0
		AND (acad_group = 'BUS' or  acad_org = '830H')
	)
GROUP BY course_id, course_code, course_name, term_code, acad_career, school_code, college, campus
ORDER BY course_id, course_code, term_code
'''.format(st_term, end_term)
  return qry


# get data from sams
sams_qry = qry_course_details(st_term=st_term, end_term=end_term)

try:
  df = pd.read_sql(sql=sams_qry, con=sams_engine)
except:
  print(sams_qry)

print(len(df))

#x = postgres_con.execute(qry_delete_after_term(schema='courses',
#                                               table='tbl_course_details',
#                                               term_code=st_term),
#                         )

df.to_sql(name='tbl_course_details',
          con=postgres_engine,
          schema='courses',
          if_exists='append',
          index=False
          )

# Add update statement to table description
date = dt.datetime.now().date()
qry_comment = """
COMMENT ON TABLE lookups.tbl_course_details
    IS 'Updated on {0} for {1} to {2}'
;
""".format(date.strftime('%d-%m-%Y'), st_term, end_term)

print(qry_comment)
trans = postgres_con.begin()
postgres_con.execute(qry_comment)
trans.commit()



