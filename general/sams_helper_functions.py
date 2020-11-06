### SAMS HELPER FUNCTIONS FOR PETER August 2018
## Provides self-contained set of functions to connect to the SAMS reporting database
## You can connect either as a CURSOR, an ENGINE, or a SESSION. 
## You always need to supply the password, but the SAMS functions do the work of supplying the connection details. 
## Dependency packages: 'cx_Oracle' and 'sqlalchemy'

import os
import sys
import numpy
import traceback
import cx_Oracle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

def return_sams_cursor(password_str=None):
  """
  This is one of three connection shortcut functions for the SAMS reporting database. 
  A CURSOR can execute SQL as if you were in a database GUI. 
  However, you cannot use a cursor with Pandas functions (you would use an Engine for this)
  Also it is difficult to control the flow of commits for database management with a cursor (you would use a Session for this)  
  This function returns a CURSOR object for the SAMS reporting database.
  The cursor can allow queries, but not commits. 
  If there is any error, it returns False.
  """
  result = False
  try:
    sams_engine = return_sams_engine(password_str=password_str)
    sams_conn = sams_engine.raw_connection()
    sams_cursor = sams_conn.cursor()
    return(sams_cursor)
  except:
    traceback.print_exc()
    return(result)

def return_sams_engine(password_str=None):
  """
  This is one of three connection shortcut functions for the SAMS reporting database. 
  It is also important part of the hierarchy: an engine can be used to initiate a cursor or a session.
  An ENGINE is sometimes called 'con' or 'conn'
  You can't execute SQL directly with an engine, but you can use it with PANDAS functions that do (pass it in where you see the 'con' argument)
  This function returns an ENGINE object for the SAMS reporting database.
  If there is any error, it returns False.
  """
  result = False
  try:
    sams_details = return_sams_details()
    engine_string = 'oracle+cx_oracle://{}:{}@{}'.format(sams_details["user_str"], password_str, sams_details["connection_identifier"])
    sams_engine = create_engine(engine_string)
    return(sams_engine)
  except:
    traceback.print_exc()
    return(result)

    db_engine = return_rmit_engine(database_name=database_name, password_str=password_str)
    db_conn = db_engine.raw_connection()



def return_sams_session(password_str=None):
  """
  This is one of three connection shortcut functions for the SAMS reporting database. 
  SESSIONS can be used (mostly) like cursors. 
  Sessions have the advantage of having optional commits. 
  Sessions are great for managing updates of a database.
  For SAMS reporting database, they might not be as useful as you won't be making updates.
  This function returns a session object for the SAMS reporting database.
  If there is any error, it returns False.
  """
  result = False
  try:
    sams_engine = return_sams_engine(password_str=password_str)
    print(sams_engine)
    Session = sessionmaker(bind=sams_engine)
    current_session = Session()
    return(current_session)
  except:
    traceback.print_exc()
    return (result)

def return_sams_details():
  """
  Function used by other functions above.
  Shortcut to just return SAMS reporting database connection details, as a dictionary. This does not include the password.
  This function is used by the other SAMS related functions to supply the full connection details.
  You need to provide the password elsewhere (when calling the sams_engine, sams_session, or sams_cursor functions)
  It won't work if you have a firewall to the SAMS reporting database from your machine.
  """
  print("Fetching SAMS reporting database connection details (except password)...")    
  sams_details = {}    
  sams_details["trusted_connection"] = False
  sams_details["db_type"] = 'oracle'
  sams_details["address_type"] = 'service'
  sams_details["user_str"] ='sqlproxy'
  sams_details["connection_identifier"] = '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=samsprddb02.int.its.rmit.edu.au)(PORT=1521))(CONNECT_DATA=(SERVER=dedicated)(SERVICE_NAME=PSCSPRD.its.rmit.edu.au)))'
  return(sams_details)


def db_extract_query_to_dataframe(sql_query, cur, print_messages=False):
  """
  This function extracts a query from a database, into a Pandas dataframe with headers.
  If it encounters an error, it exits and returns False.
  Otherwise, it returns the SQL query results in a dataframe.
  Input: SQL string, cursor with connection to database.
  Ouput (when no error encountered): dataframe containing all the query results.
  Output (when error encountered): False
  Note: No need to specify schema name, as the query may extend across multiple schemas.
  Note: This previously returned an empty array on error, in Jan 2018 it was modified to return False, just for consistency across RMIT studios scripts.
  """
  
  result = False
  try:
    # Extract SQL query
    if (print_messages == True):
      print("Sending query:")
      print(sql_query)
    
    cur.execute(sql_query)
    
    # pass SQL result to dataframe named 'df'
    df = pd.DataFrame(cur.fetchall())
    df.columns = [i[0] for i in cur.description]
    return (df)
  
  except:
    # print(sql_query)
    # traceback.print_exc()
    return (result)
  

def connect_to_postgres_db(con_string):
  """
  This function creates a connection to a postgres database
  :param con_string:
  :return:
  """
  import psycopg2
  # get a connection, if a connect cannot be made an exception will be raised here
  con = psycopg2.connect(con_string)
  # conn.cursor will return a cursor object, you can use this cursor to perform queries
  cur = con.cursor()
  return con, cur

def convert_list_string_for_sql(list1):
  txt = '('
  for str in list1:
    txt += "'{0}', ".format(str)
  # Drop final comma and add )
  txt = txt[:-2]
  txt += ') '
  return txt

def get_term_category(location, semester=None):
  if semester != None:
    if location == 'MELB':
      return [current_semester]
    if location == 'SBM':
      return [current_semester+4]
    if location == 'SIM':
      if semester == 1:
        return[5]
      if semester == 2:
        return [7]
    else:
      print('Selection not available')
      return None

  if semester == None:
    if location == 'MELB':
      return [1, 2]
    if location == 'SBM':
      return [5, 6, 7]
    if location == 'SIM':
      return [5, 7]
    else:
      print('Selection not available')
      return None


def get_term_code_ends(location, semester=None, level='VE'):
  if location == 'MELB':
    if level == 'VE':
      x = ['05', '45']
    if level == 'HE':
      x = ['10', '50']
  
  if location == 'SIM':
    x = ['20', '60']
  
  if location in ['SBM', 'VN']:
    x = ['91', '92', '93']
  
  if location in ['CSI', 'SUIBE']:
    x = ['08', '48', '20', '30', '60']
  
  try:
    if semester == None:
      return x
    
    else:
      return [x[semester - 1]]
  
  except:
    print('Selection not available')
    return None