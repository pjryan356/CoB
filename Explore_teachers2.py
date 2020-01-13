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

custom_palette = sns.color_palette([rc.RMIT_White, rc.RMIT_Blue2, rc.RMIT_Green3, rc.RMIT_White])
custom_palette2 = sns.color_palette([rc.RMIT_White, rc.RMIT_Blue, rc.RMIT_Green, rc.RMIT_White])
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
#postgres_pw = input("Postgres Password: ")
postgres_pw = 'London2012'
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

def get_course_teacher_ces(cur, tbl='vw811_teacher_data', schema='ces'):
  # Returns a dataframe with change in CES data for 2019
  qry = ' SELECT \n' \
        "    t1.*, LEFT(RIGHT(teaching_staff,7),6) AS emplid \n" \
        ' FROM {0}.{1} t1 \n' \
        ' WHERE t1.teacher_count > 5 \n' \
        " ORDER BY t1.teaching_staff, t1.year, t1.semester, t1.type".format(schema, tbl)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)

def get_teachers(cur, tbl='vw810_teacher_data_agg', schema='ces'):
  # Returns a dataframe with change in CES data for 2019
  qry = ' SELECT \n' \
        "   LEFT(RIGHT(teaching_staff,7),6) AS emplid, teaching_staff, avg_gts, avg_crse_gts, avg_gts-avg_crse_gts AS avg_gts_diff \n" \
        ' FROM {0}.{1} \n' \
        ' WHERE count_2019 > 0 AND count >= 5 \n' \
        " ORDER BY avg_gts; \n" \
        "".format(schema, tbl)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


'''-------------------------------------------- Create Dataframes -------------------------------------'''

df = get_course_teacher_ces(cur=postgres_cur, tbl='vw811_teacher_data', schema='ces')
df2 = get_teachers(cur=postgres_cur, tbl='vw810_teacher_data_agg', schema='ces')
step = 12
sns.set_style("darkgrid")
dims = (10, 5)
j = 0
folder='H:\\Projects\\CoB\\CES\\Teachers\\'
for i in range(0, step*19+1, step):
  j+=1

  fig, ax = plt.subplots(figsize=dims)

  #print(tabulate(df2[i:i+step], headers='keys'))
  teachers = df2[i:i+step]['emplid'].tolist()

  
  sns.swarmplot('emplid', 'gts', ax=ax,
                data=df.loc[(df['emplid'].isin(teachers))],
                order=teachers, hue='type', hue_order=['A', 'Staff', 'Course', 'Z'], palette=custom_palette,
                edgecolor=rc.RMIT_Black, linewidth=0.5,
                size=5,
                dodge=True)
  
  sns.swarmplot('emplid', 'gts', ax=ax,
                data=df.loc[(df['emplid'].isin(teachers) & (df['year'].isin([2019])))],
                order=teachers, hue='type', hue_order=['A', 'Staff', 'Course', 'Z'], palette=custom_palette2,
                edgecolor=rc.RMIT_Black, linewidth=0.5,
                size=5,
                dodge=True)
  
  '''
  sns.stripplot('emplid', 'gts', ax=ax,
                data=df.loc[(df['emplid'].isin(teachers)) & (df['type']=='Staff') & (df['year'].isin([2019]))],
                order=teachers, hue='year', palette=sns.color_palette([rc.RMIT_Blue]),
                edgecolor=rc.RMIT_White, linewidth=0.5,
                size=5, jitter=False)
  '''
  # Get the handles and labels.
  handles, labels = ax.get_legend_handles_labels()
  # When creating the legend,
  l = plt.legend([handles[1], handles[5], handles[2], handles[6]], ['Teacher', 'Teacher 2019', 'Whole Course', 'Course 2019'], loc='lower right')
  #x = plt.xticks(rotation=30)

  ax.axes.set_title("Teacher/Course GTS comparison (2015-2019)", fontsize=16)
   
  ax.set_xlabel("Employee ID", fontsize=14)
   
  ax.set_ylabel("Percent Agree", fontsize=14)
  
  ax.set_ylim([0, 105])
  plt.subplots_adjust(left=0.07, bottom=0.1, right=0.97, top=0.93)

  fig.savefig(folder+"teacher_gts_swarm_{:02d}.png".format(j))
