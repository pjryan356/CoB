## Creates course assessment files for CAC purposes
# Peter Ryan Nov 2018

import pandas as pd
import sys
import re
import os
import psycopg2
from sqlalchemy import (create_engine, orm)
from tabulate import tabulate

sys.path.append('c:\\Peter\\GitHub\\CoB\\')

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


# open CLOs worksheet
directory = 'C:\\Peter\\CLOs 2020\\'
clo_filename = 'load_extras.csv'
master_list = []

df = pd.read_csv(open(directory+clo_filename, 'rb'), "CLO (Alt)", converters={'course_id': str})

#df = pd.DataFrame(master_list, columns = ['course_id', 'clo_nbr', 'clo_text', 'updated'])

'''
print(tabulate(df, headers='keys'))
df.to_sql(name='clo',
            con=postgres_engine,
            schema='courses',
            if_exists='append',
            index=False
          )
'''
