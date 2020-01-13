## Load CES course_program data excel files downloaded from Survey Team google drive
# Peter Ryan October 2018

import pandas as pd
from sqlalchemy import (create_engine)
from tabulate import tabulate
import datetime as dt


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


def upload_ce_tracking_data_from_excel(directory, filename, engine, tbl_name='tbl_course_tracking',
                                       schema='course_enhancement'):
  # get data from excel file
  df = pd.read_excel(directory + filename,
                     sheet_name='data',
                     skiprows=0,
                     usecols=[0, 1, 4, 5, 7,
                              10, 11, 12, 13],
                     skipfooter=0)
  
  df.columns = ['cycle', 'course_code_ces', 'school', 'wave', 'status',
                'support_offered', 'support_staff', 'ctl', 'notes']
  df = df.infer_objects()
  
  # seperate support staff into individual rows
  df2 = pd.DataFrame()
  for i, row in df.iterrows():
    x = None
    try:
      x = row['support_staff'].split(';#')
      for j in range(0, len(x), 2):
        row['support_staff'] = x[j]
        df2 = df2.append(row)
    except:
      row['support_staff'] = None
      df2 = df2.append(row)
  
  # seperate support offered into individual rows
  df3 = pd.DataFrame()
  
  for i, row in df2.iterrows():
    x = None
    try:
      x = row['support_offered'].split(';#')
      for j in range(0, len(x), 1):
        row['support_offered'] = x[j]
        df3 = df3.append(row)
    except:
      row['support_offered'] = None
      df3 = df3.append(row)
  
  # reorder columns
  df3 = df3[[
    'cycle', 'course_code_ces', 'school',
    'wave', 'status',
    'support_offered', 'support_staff',
    'ctl', 'notes']]

  print(tabulate(df3.loc[df3['cycle'].notnull()], headers='keys'))

  
  try:
    trans = postgres_con.begin()
    # clear old table
    qry = 'DELETE FROM course_enhancement.tbl_course_tracking'
    postgres_con.execute(qry)
    
    
    # upload new data into database
    df3.loc[df3['cycle'].notnull()].to_sql(
      name=tbl_name,
      con=engine,
      schema=schema,
      if_exists='append',
      index=False
    )
  
    # Add update statement to table description
    date = dt.datetime.now().date()
    qry_comment = """
    COMMENT ON TABLE enrolments.tbl_class_program_pop
    IS 'Data from the Course Enhancement Sharepoint\n
    Updated on {0}'
    ;
    """.format(date.strftime('%d-%m-%Y'))
    
    postgres_con.execute(qry_comment)
    trans.commit()
  except:
    raise


# get data from excel doc
# open template
directory = 'H:\\Projects\\CoB\\CES\\Course Enhancement\\'
filename = 'Course_Enhancement_All.xlsx'

upload_ce_tracking_data_from_excel(directory, filename, postgres_engine)


