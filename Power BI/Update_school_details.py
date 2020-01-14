## Upload School details files to Onedrive for use in Power BI
# Peter Ryan Nov 2018

import pandas as pd
import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
)

'''--------------------------------- Connect to Database  ----------------------------'''
# create postgres engine this is the connection to the postgres database
postgres_pw = input("Postgres Password: ")
postgres_user = 'pjryan'
postgres_host = 'localhost'
postgres_dbname = 'postgres'

con_string = "host='{0}' " \
             "dbname='{1}' " \
             "user='{2}' " \
             "password='{3}' " \
             "".format(postgres_host, postgres_dbname, postgres_user, postgres_pw)

postgres_con, postgres_cur = connect_to_postgres_db(con_string)


def get_table(cur, schema, tbl):
  # Returns all values in a table
  qry = 'SELECT * FROM {}.{}'.format(schema, tbl)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


df = get_table(postgres_cur, schema='lookups', tbl='vw_bus_schools_colours')

df.to_csv('C:\\Users\\e35137\\OneDrive - RMIT University\\L&T Data\\Power BI files\\Schools.csv')

