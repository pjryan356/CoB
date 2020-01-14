import base64
import flask
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import traceback

from collections import OrderedDict
from tabulate import tabulate
import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc
'''
sns.swarmplot(y = "city",
              x = 'O3',
              data = pollution_mar,
              # Decrease the size of the points to avoid crowding
              size = 3)

# Give a descriptive title
plt.title('March Ozone levels by city')
plt.show()
'''

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


def get_course_ce_ces_change(cur, tbl='vw500_course_tracker_ces_reliable', schema='course_enhancement'):
  # Returns a dataframe with change in CES data for 2019
  qry = ' SELECT \n' \
        "   * \n" \
        ' FROM {0}.{1} \n' \
        " WHERE year = 2019 AND semester = 2 AND status >= '6' ; \n" \
        "".format(schema, tbl)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)



'''-------------------------------------------- Create Dataframes -------------------------------------'''

def plot_status():
  sns.set_style('darkgrid')
  
  qry = 'SELECT * \n' \
        'FROM course_enhancement.vw510_course_tracker_ces_reliable_status \n' \
        'WHERE  year = 2019 AND semester = 2' \
        '   AND ce IS NOT NULL\n'
  
  df_status = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)
  
  df_status['osi_delta'] = df_status['osi_delta'].astype('float')
  df_status['gts_delta'] = df_status['gts_delta'].astype('float')
  
  df_status = df_status.sort_values('status_original')
  df_status = df_status.loc[df_status['status'] != 'Further Support Required']
  
  palette = sns.color_palette([rc.RMIT_Purple, rc.RMIT_Blue, rc.RMIT_DarkBlue, rc.RMIT_Teal])
  # Extra catagory: 'Further Support Required'
  # Extra color: rc.RMIT_Pink
  
  print(tabulate(df_status, headers='keys'))
  
  order = ['No Engagement',
           'Received Support',
           'Completed CLT',
           'No Support Required']
  
  fig = sns.relplot(y='gts_delta', x='osi_delta', data=df_status,
                    height=3,
                    kind='scatter',
                    col='status',
                    hue='status',
                    legend=False,
                    col_wrap=2,
                    palette=palette)

  for i, ax in enumerate(fig.axes):
    ax.plot([0, 0], [-35, 45], color='black')
    ax.plot([-35, 45], [0, 0], color='black')
    ax.plot([-35, 45], [-35, 45], color=rc.RMIT_Red, linestyle='--')
    ax.set_title(order[i])
  
  fig.set_axis_labels('Change in OSI', 'Change in GTS')
  plt.show()


def plot_status2():
  sns.set_style('darkgrid')
  
  qry = 'SELECT * \n' \
        'FROM course_enhancement.vw510_course_tracker_ces_reliable_status \n' \
        'WHERE  year = 2019 AND semester = 2 \n' \
        "   AND ce IS NOT NULL \n" \
        "   AND gts_delta >= -30 \n" \
        "   AND gts_delta <= 30 \n"
  df_status = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)
  
  df_status['osi_delta'] = df_status['osi_delta'].astype('float')
  df_status['gts_delta'] = df_status['gts_delta'].astype('float')
  
  df_status = df_status.sort_values('status_original')
  df_status = df_status.loc[df_status['status'] != 'Further Support Required']
  
  palette = sns.color_palette([rc.RMIT_Purple, rc.RMIT_Blue, rc.RMIT_DarkBlue, rc.RMIT_Teal])
  # Extra catagory: 'Further Support Required'
  # Extra color: rc.RMIT_Pink
  
  print(tabulate(df_status, headers='keys'))
  
  order = ['No Engagement',
           'Received Support',
           'Completed CLT',
           'No Support Required']

  fig, ax = plt.subplots(1, 1)

  sns.catplot(y='status', x='gts_delta', data=df_status, hue='status', ax=ax,
              kind='point',
              order=order,
              hue_order=order,
              palette=palette)

  sns.catplot(y='status', x='gts_delta', data=df_status, hue='status', ax=ax,
              kind='strip',
              order=order,
              hue_order=order,
              palette=palette,
              jitter=0.25, alpha=0.5)

  ax.get_legend().remove()

  ax.set_xlabel('Change in GTS')
  ax.set_ylabel('')
  #ax.set_title('Type of Support')
  plt.show()
  

def plot_support():
  sns.set_style('darkgrid')
  qry = ' SELECT * \n' \
        ' FROM course_enhancement.vw520_course_tracker_ces_reliable_support \n' \
        ' WHERE  year = 2019 AND semester = 2 \n' \
        "   AND support_offered NOT IN ('UNK', 'None')" \
        "   AND ce IS NOT NULL \n" \
        "   AND gts_delta >= -30 \n" \
        "   AND gts_delta <= 30 \n"
  
  df_support = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)
  
  df_support['osi_delta'] = df_support['osi_delta'].astype('float')
  df_support['gts_delta'] = df_support['gts_delta'].astype('float')
  df_support = df_support.sort_values('support_offered')
  
  print(tabulate(df_support, headers='keys'))
  
  order = ['Canvas Support',
           'Learning Design (Canvas)',
           'Learning Design',
           'Assessment',
           'Liaison Librarian',
           'Referred back to School',
           'Referred to Industry Engagement',
           'Production'
           ]
  
  palette2 = sns.color_palette([rc.RMIT_Red, rc.RMIT_Yellow, rc.RMIT_Orange, rc.RMIT_Green, rc.RMIT_Aqua,
                                rc.RMIT_Arctic, rc.RMIT_Azure, rc.RMIT_Blue, rc.RMIT_Purple,
                                rc.RMIT_Lavender])

  fig, ax = plt.subplots(1,1)

  sns.catplot(y='support_offered', x='gts_delta', data=df_support, hue='support_offered', ax=ax,
              kind='point',
              order=order,
              hue_order=order,
              palette=palette2)

  sns.catplot(y='support_offered', x='gts_delta', data=df_support, hue='support_offered', ax=ax,
              kind='strip',
              order=order,
              hue_order=order,
              palette=palette2,
              jitter=0.25, alpha=0.5)

  ax.get_legend().remove()
  
  ax.set_xlabel('Change in GTS')
  ax.set_ylabel('')
  #ax.set_title('Type of Support')
  plt.show()
  
  # f = sns.catplot(x='support_offered', y='gts_delta', hue='status', data=df,
  #                kind='box', dodge=True)
  
def plot_empty_scatter():
  
  ax = plt.plot([0, 0], [-35, 45], color='black')
  plt.plot([-35, 45], [0, 0], color='black')
  plt.plot([-35, 45], [-35, 45], color=rc.RMIT_Red, linestyle='--')
  
  plt.annotate('Increase in GTS\nDecrease in OSI',
               xy=(0.1, 0.7), xycoords='axes fraction')
  
  plt.annotate('Increase in GTS\nIncrease in OSI',
               xy=(0.6, 0.70), xycoords='axes fraction')
  
  plt.annotate('Decrease in GTS\nIncrease in OSI',
               xy=(0.6, 0.2), xycoords='axes fraction')
  
  plt.annotate('Decrease in GTS\nDecrease in OSI',
               xy=(0.1, 0.2), xycoords='axes fraction')
  
  plt.annotate('Change in GTS = Change in OSI',
               xy=(0.5, 0.9), xycoords='axes fraction',
               color=rc.RMIT_Red,
               rotation=37)

  plt.annotate('Change in GTS = Change in OSI',
               xy=(0.5, 0.9), xycoords='axes fraction',
               color=rc.RMIT_Red,
               rotation=37)

  plt.show()
  
  
plot_support()
plot_status2()