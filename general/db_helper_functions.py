## DATABASE HELPER FUNCTIONS
# Peter November 2018
# I am putting together Database function from different places

import traceback
import pandas as pd


def objectlist_to_text(obList):
  # converts a list of object into a string list for sql IN statement
  txt = "("
  for ob in obList:
    txt += "'{}', ".format(ob)
  txt = txt[:-2] + ")"
  return txt

def convert_list_string_for_sql(list1):
  txt = '('
  for str in list1:
    txt += "'{0}', ".format(str)
  # Drop final comma and add )
  txt = txt[:-2]
  txt += ') '
  return txt

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
    return df
  
  except:
    print(sql_query)
    traceback.print_exc()
    return result

def get_school_name(school_code):
  if school_code == '610P':
    return 'CBO'
  if school_code == '615H':
    return 'ACCT'
  if school_code == '620H':
    return 'BITL'
  if school_code == '625H':
    return 'EFM'
  if school_code == '630H':
    return 'MGT'
  if school_code == '650T':
    return 'VBE'
  if school_code == '660H':
    return 'GSBL'
  if school_code == 'VN':
    return 'Not CoB'
  return None

def get_campus_list_string(location):
  if location == 'MELB':
    return None
  
  if location == 'SIM':
    return "('SGPIM')"
  
  if location in ('CSI', 'SUIBE'):
    return "('CHNSI')"
  
  if location in ('SBM', 'VN'):
    return "('VNMRH', 'VNMRI')"
  