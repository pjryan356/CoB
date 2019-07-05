import base64
import flask
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


from collections import OrderedDict
from tabulate import tabulate
import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc



'''--------------------------------- Connect to Database  ----------------------------'''

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


'''------------------------------ Helper functions -----------------------------------'''
def get_course_pop(df1, course_code, term_code=None, year=None, semester=None):
  if term_code != None:
    try:
      df1_filter = df1.loc[
        (df1['term_code'] == term_code) &
        (df1['course_code_ces'] == course_code)]
      pop = int(df1_filter['population'].agg('sum'))
      return (pop)
    except:
      return None
  else:
    try:
      df1_filter = df1.loc[
        (df1['year'] == year) &
        (df1['semester'] == semester) &
        (df1['course_code_ces'] == course_code)]
      
      pop = int(df1_filter['population'].agg('sum'))
      return (pop)
    except:
      return None
    

def list_to_text(obList):
  # converts a list of object into a string list for sql IN statement
  txt = "("
  for ob in obList:
    txt += "'{}',".format(ob)
  txt = txt[:-1] + ")"
  return txt

'''----------------------------- create data extraction functions -------------------------------------'''

def get_course_sim_ces_data_programs(cur, tbl='vw201_course_prg', schema='sim_ces'):
  # Returns a dataframe with SIM CES data for courses in course list
  qry = ' SELECT \n' \
        "   year, semester, concat(year, ' S', semester) AS sem, \n" \
        "   school, \n" \
        "   program_code, \n" \
        "   ams_block_nbr, \n" \
        "   course_code, course_name, \n" \
        "   staff_type, \n" \
        '   responses, population, \n' \
        '   subject_content, \n' \
        '   lecturer_effectiveness, \n' \
        '   course_satisfaction \n ' \
        ' FROM {0}.{1} \n' \
        " ORDER BY year, semester; \n" \
        "".format(schema, tbl)
  
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


def get_course_sim_ces_data_programs_2(cur, tbl='vw202_course_prg', schema='sim_ces'):
  # Returns a dataframe with SIM CES data for courses in course list
  qry = ' SELECT \n' \
        "   year, semester, concat(year, ' S', semester) AS sem, \n" \
        "   school, \n" \
        "   program_code, \n" \
        "   ams_block_nbr, \n" \
        "   course_code, course_name, \n" \
        '   responses, population, \n' \
        '   subject_content, \n' \
        '   lecturer_effectiveness, \n' \
        '   course_satisfaction \n ' \
        ' FROM {0}.{1} \n' \
        " ORDER BY year, semester; \n" \
        "".format(schema, tbl)
  
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)

def get_sim_course_data(df1, course_code):
  # filters dataframe to given course_code
  try:
    return df1.loc[df1['course_code'] == course_code]
  except:
    pass
  return None

'''-------------------------------------------- Create Dataframes -------------------------------------'''

df = get_course_sim_ces_data_programs(cur=postgres_cur)
df['subject_content'] = df['subject_content'].astype('float')
df['lecturer_effectiveness'] = df['lecturer_effectiveness'].astype('float')
df['course_satisfaction'] = df['course_satisfaction'].astype('float')
print(tabulate(df[:10], headers='keys'))

df2 = get_course_sim_ces_data_programs_2(cur=postgres_cur)
df2['subject_content'] = df2['subject_content'].astype('float')
df2['lecturer_effectiveness'] = df2['lecturer_effectiveness'].astype('float')
df2['course_satisfaction'] = df2['course_satisfaction'].astype('float')
print(tabulate(df2[:10], headers='keys'))


for program_code in ["BP217", "BP251", "BP252", "BP253", "BP254", "BP255", "CC000"]:
  f = sns.catplot(x='sem', y='lecturer_effectiveness', data=df.loc[(df['program_code'] == program_code)],
                  kind='box', hue='staff_type')

  f.fig.suptitle("{} SIM CES: Lecturer Effectiveness".format(program_code), y=0.98)
  plt.xticks(rotation=45)
  f.set(ylabel="Course Means", xlabel='')

  g = sns.catplot(x='sem', y='subject_content', data=df2.loc[(df2['program_code'] == program_code)],
                  kind='box')

  sns.stripplot(x="sem", y="subject_content", data=df2.loc[(df2['program_code'] == program_code)],
              size=4, jitter=True, edgecolor="black")

  g.fig.suptitle("{} SIM CES: Subject Content".format(program_code), y=0.98)
  plt.xticks(rotation=45)
  g.set(ylabel="Course Means", xlabel='')

  h = sns.catplot(x='sem', y='course_satisfaction', data=df2.loc[(df2['program_code'] == program_code)
                                                                 & (df2['course_satisfaction'] >= 3.0)],
                  kind='box',
                  palette=sns.color_palette()[1:])

  sns.stripplot(x="sem", y="course_satisfaction", data=df2.loc[(df2['program_code'] == program_code)
                                                               & (df2['course_satisfaction'] >= 3.0)],
                size=4, jitter=True, edgecolor="gray",
                palette=sns.color_palette()[1:])

  h.fig.suptitle("{} SIM CES: Course Satisfaction".format(program_code), y=0.98)
  plt.xticks(rotation=45)
  h.set(ylabel="Course Means", xlabel='')

  h.axes[0, 0].set_ylim(3.5, 4.5)
  g.axes[0, 0].set_ylim(3.5, 4.5)
  f.axes[0, 0].set_ylim(3.5, 4.5)
  
  plt.show()

'''
f = sns.catplot(x='sem', y='lecturer_effectiveness', data=df,
                  kind='box', hue='staff_type')

#sns.stripplot(x="sem", y="course_satisfaction", data=df,
#              size=4, jitter=True, edgecolor="gray")

f.fig.suptitle("RMIT SIM CES: Lecturer Effectiveness", y=0.98)
plt.xticks(rotation=45)
f.set(ylabel="Course Means", xlabel='')

f = sns.catplot(x='sem', y='subject_content', data=df,
                  kind='box', hue='staff_type')

#sns.stripplot(x="sem", y="subject_content", data=df,
#              size=4, jitter=True, edgecolor="gray")

f.fig.suptitle("RMIT SIM CES: Subject Content", y=0.98)
plt.xticks(rotation=45)
f.set(ylabel="Course Means", xlabel='')

f = sns.catplot(x='sem', y='course_satisfaction', data=df,
                  kind='box', hue='staff_type')

#sns.stripplot(x="sem", y="course_satisfaction", data=df,
#              size=4, jitter=True, edgecolor="gray")

f.fig.suptitle("RMIT SIM CES: Course Satisfaction", y=0.98)
plt.xticks(rotation=45)
f.set(ylabel="Course Means", xlabel='')

f = sns.catplot(x='sem', y='course_satisfaction', data=df,
                  kind='box', hue='staff_type')

#sns.stripplot(x="sem", y="course_satisfaction", data=df,
#              size=4, jitter=True, edgecolor="gray")

f.fig.suptitle("RMIT SIM CES: Course Satisfaction", y=0.98)
plt.xticks(rotation=45)
f.set(ylabel="Course Means", xlabel='')
plt.show()
'''

