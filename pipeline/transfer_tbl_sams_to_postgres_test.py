## Test script to upload data from SAMS into local db
# Peter Ryan Nov 2018

import pandas as pd
import tabulate
import datetime as dt
import psycopg2

sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc
from general.sams_queries import *

from general.db_helper_functions import(
  connect_to_postgres_db
)

from general.postgres_queries import (
  qry_create_table_course_location,
  qry_add_comment,
  qry_drop_table)

# Input parameters
year = 2019
semester = 1
level = 'NA'

# Create connections
postgres_pw = input("Postgres Password: ")
sams_pw = input("SAMS Password: ")

# create sams engine this is the connection to the oracle database
sams_engine = return_sams_engine(password_str=sams_pw)

result_dataframe = pd.read_sql(sql=qry_sams_course_locations(), con=sams_engine)

print(tabulate.tabulate(result_dataframe, headers='keys'))


'''--------------------------------- Connect to Database  ----------------------------'''
con_string = "host='localhost' " \
             "dbname='postgres' " \
             "user='pjryan' " \
             "password='{}'".format(postgres_pw)

conn, cur = connect_to_postgres_db(con_string)

try:
  cur.execute(qry_drop_table(schema='ms', table='course_locations'))
  cur.execute(qry_create_table_course_location(schema='ms', table='course_locations'))
  cur.execute(qry_add_comment(schema='ms',
                              table='course_locations',
                              comment='Updated on {}'.format(dt.datetime.now().date().strftime('%d/%m/%Y'))
                              )
              )
  # commit the changes
  conn.commit()
  
except (Exception, psycopg2.DatabaseError) as error:
  print(error)

for i, r in result_dataframe.iterrows():
  qry = '''
  INSERT INTO
    ms.course_locations(
      year, semester, level, course_id, course_code_ms, campus_ms, cc_city, cc_brunswick, cc_bundoora, cc_aus_online,
      cc_singapore_im, cc_singapore_kp, cc_china_shanghai, cc_china_beijing, cc_hk_ac, cc_hk_vt, cc_ausvn, cc_vtn_ri,
      cc_vtn_pa, cc_vtn_rh, cc_uph, cc_www_ou, cc_www_kp)
  VALUES ({}, {}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
   '{}', '{}', '{}', '{}', '{}', '{}');
  '''.format(year, semester, level, r.course_id, r.course_code_ms, r.campus_ms,
             r.city, r.brunswick, r.bundoora, r.aus_online, r.singapore_im, r.singapore_kp,
             r.china_shanghai, r.china_beijing, r.hongkong_ac, r.hongkong_vt, r.ausvn,
             r.veitnam_ri, r.veitnam_pa, r.veitnam_rh , r.uph, r.www_ou, r.www_kp)
  print(qry)
  cur.execute(qry)
  
conn.commit()

'''
### Get microsurgery courses
qry = " SELECT DISTINCT \n" \
      "   ms.level, ms.school_code, ms.course_code, SPLIT_PART(ms.course_code,'-', 1) AS course_code_alt," \
      "   cd.school_name, cd.course_name \n" \
      " FROM (" \
      "   SELECT level, school_code, course_code \n" \
      "	  FROM projects.microsurgery_list \n" \
      "   WHERE year = {0} AND semester = {1} \n" \
      "   ) ms \n" \
      " LEFT OUTER JOIN ( \n" \
      "   SELECT * FROM lookups.vw_course_details_recent \n" \
      "   ) cd ON (SPLIT_PART(cd.course_code,'-', 1) = SPLIT_PART(ms.course_code,'-', 1))\n" \
      " ORDER BY ms.school_code, ms.course_code \n" \
      "".format(year, semester)

df_ms = db_extract_query_to_dataframe(qry, cur, print_messages=False)
'''