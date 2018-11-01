from tabulate import tabulate
import traceback
import pandas as pd

import RMIT_colours as rc
colourList = [rc.RMIT_Red,
              rc.RMIT_Green,
              rc.RMIT_Blue,
              rc.RMIT_Orange,
              rc.RMIT_Purple,
              rc.RMIT_Yellow,
              rc.RMIT_DarkBlue,
              rc.RMIT_Pink,
              rc.RMIT_Black,
              rc.RMIT_Aqua,
              rc.RMIT_Lemon,
              rc.RMIT_Lavender,
              rc.RMIT_Azure,
              rc.RMIT_Teal,
              rc.RMIT_Arctic
              ]
'''--------------------------------- Common Functions ----------------------------------'''
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
    return (df)
  
  except:
    print(sql_query)
    traceback.print_exc()
    return (result)
  
def get_term_name(term_code, year=None, semester=None, level=None, short=False):
  '''
  :param term_code: RMIT term code
  :return: string 'Year Term_name'
  '''
  txt = ''
  try:    year = '20{}'.format(term_code[:2])
  except: year = ''

  try:
    term_txt = ''
    term = term_code[2:]
    if short == False:
      if term == '00':
          term_txt = 'Summer Semester'
      elif term in ['01', '03']:
          term_txt = 'Academic Year'
      elif term == '02':
          term_txt = 'Flexible Term'
      elif term in ['05', '10']:
          term_txt = 'Semester 1'
      elif term in ['45', '50']:
          term_txt = 'Semester 2'
      elif term == '20':
          term_txt = 'Offshore Semester 1'
      elif term == '30':
          term_txt = 'Offshore Semester 2'
      elif term == '60':
          term_txt = 'Offshore Semester 3'
      elif term == '70':
          term_txt = 'Offshore Semester 4'
      elif term == '78':
          term_txt = 'Spring Semester'
      elif term == '91':
          term_txt = 'Vietnam Semester 1'
      elif term == '92':
          term_txt = 'Vietnam Semester 2'
      elif term == '93':
          term_txt = 'Vietnam Semester 3'
  
    if short == True:
      if term in ['05', '10', '91', '20']:
        term_txt = 'S1'
      elif term in ['45', '50', '92', '60']:
        term_txt = 'S2'
      elif term in ['93']:
        term_txt = 'S3'
      else:
        term_txt = 'Irregular offering'
       
  except:
    term_txt = ''
  
  output = ''
  output += year
  
  if term_txt != '':
    output += ' {}'.format(term_txt)
  return output

def get_colour(measure, level = 'HE'):
  if measure == 'osi':
    return rc.RMIT_Green
  if measure == 'gts':
    return rc.RMIT_DarkBlue

  if level == 'HE':
    #  Perceived Effort
    if measure == 'gts2':
      return rc.RMIT_Red
    if measure == 'gts5':
      return rc.RMIT_Pink
    if measure == 'gts6':
      return rc.RMIT_Orange
    
    # Student Engagement (Impact)
    if measure == 'gts3':
      return rc.RMIT_Blue
    if measure == 'gts4':
      return rc.RMIT_Azure
    if measure == 'gts1':
      return rc.RMIT_Aqua


  if level == 'VE':
    
    # Student Engagement (Practise)
    if measure == 'gts2':
      return rc.RMIT_Purple
    if measure == 'gts3':
      return rc.RMIT_Lavender
    
    # Perceived Capability
    if measure == 'gts1':
      return rc.RMIT_Red
    if measure == 'gts4':
      return rc.RMIT_Pink

    # Student Engagement (Impact)
    if measure == 'gts5':
      return rc.RMIT_Blue
    if measure == 'gts6':
      return rc.RMIT_Azure
  
  return rc.RMIT_Black

def get_course_pop(df1, term_code, course_code):
  try:
    df1_filter = df1.loc[(df1['term_code'] == term_code) &
                         (df1['course_code'] == course_code)]
    
    pop = int(df1_filter['population'].agg('sum'))
    return (pop)
  except:
    return None





