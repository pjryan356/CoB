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

def get_course_ce_ces_change(cur, tbl='vw403_change_2019s1_details', schema='course_enhancement'):
  # Returns a dataframe with change in CES data for 2019
  qry = ' SELECT \n' \
        "   * \n" \
        ' FROM {0}.{1} \n' \
        " ORDER BY year, semester; \n" \
        "".format(schema, tbl)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


'''-------------------------------------------- Create Dataframes -------------------------------------'''

df = get_course_ce_ces_change(cur=postgres_cur)
df['osi'] = df['osi'].astype('float')
df['osi_y1'] = df['osi_y1'].astype('float')
df['osi_delta'] = df['osi_delta'].astype('float')
df['gts'] = df['gts'].astype('float')
df['gts_y1'] = df['gts_y1'].astype('float')
df['gts_delta'] = df['gts_delta'].astype('float')

f = sns.catplot(x='year', y='gts_delta', data=df,
                kind='box', hue='ce')
f.fig.suptitle("CoB: Course Enhancement GTS comparison", y=0.98)
f.set(ylabel="Mean Course GTS (Percent Agree)", xlabel='')
plt.show()

'''
for school in ['ACCT', 'BITL', 'EFM', 'MGT']:
  f = sns.catplot(x='', y='gts', data=df.loc[(df['school'] == school)],
                  kind='box', hue='ce')

  f.fig.suptitle("{} SIM CES: Lecturer Effectiveness".format(school), y=0.98)
  plt.xticks(rotation=45)
  f.set(ylabel="Course Means", xlabel='')

  g = sns.catplot(x='sem', y='subject_content', data=df2.loc[(df2['school'] == school)],
                  kind='box')

  sns.stripplot(x="sem", y="subject_content", data=df2.loc[(df2['school'] == school)],
              size=4, jitter=True, edgecolor="gray")

  g.fig.suptitle("{} SIM CES: Subject Content".format(school), y=0.98)
  plt.xticks(rotation=45)
  g.set(ylabel="Course Means", xlabel='')

  h = sns.catplot(x='sem', y='course_satisfaction', data=df2.loc[(df2['school'] == school)
                                                                 & (df2['course_satisfaction'] >= 3.0)],
                  kind='box',
                  palette=sns.color_palette()[1:])

  sns.stripplot(x="sem", y="course_satisfaction", data=df2.loc[(df2['school'] == school)
                                                               & (df2['course_satisfaction'] >= 3.0)],
                size=4, jitter=True, edgecolor="gray",
                palette=sns.color_palette()[1:])

  h.fig.suptitle("{} SIM CES: Course Satisfaction".format(school), y=0.98)
  plt.xticks(rotation=45)
  h.set(ylabel="Course Means", xlabel='')

  
'''
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
'''
for school in ['ACCT']:
  f = sns.catplot(x='sem', y='lecturer_effectiveness', data=df.loc[(df['school'] == school)],
                  kind='box', hue='staff_type')

  f.fig.suptitle("{} SIM CES: Lecturer Effectiveness".format(school), y=0.98)
  plt.xticks(rotation=45)
  f.set(ylabel="Course Means", xlabel='')

  g = sns.catplot(x='sem', y='lecturer_effectiveness', data=df2.loc[(df2['school'] == school)],
                  kind='box')

  sns.stripplot(x="sem", y="lecturer_effectiveness", data=df2.loc[(df2['school'] == school)],
              size=4, jitter=True, edgecolor="gray")

  sns.stripplot(x="sem", y="lecturer_effectiveness", data=df.loc[(df['school'] == school)],
              size=4, jitter=True, edgecolor="gray", hue='staff_type')
  
  g.fig.suptitle("{} SIM CES: Lecturer Effectiveness".format(school), y=0.98)
  plt.xticks(rotation=45)
  g.set(ylabel="Course Means", xlabel='')
  

  plt.show()
'''