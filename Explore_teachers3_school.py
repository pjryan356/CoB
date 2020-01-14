import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')
import general.RMIT_colours as rc
from tabulate import tabulate
from numpy import NaN

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
  Note: This previously returned an empty array on error, in Jan 2018 it was modified to return False,
        just for consistency across RMIT studios scripts.
  """
  
  result = False
  try:
    # Extract SQL query
    if print_messages:
      print("Sending query:")
      print(sql_query)
    
    cur.execute(sql_query)
    
    # pass SQL result to data frame named 'df'
    df1 = pd.DataFrame(cur.fetchall())
    df1.columns = [item[0] for item in cur.description]
    return df1
  
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


def get_course_teacher_ces(cur, tbl='vw811_teacher_data', schema='ces'):
  # Returns a data frame with change in CES data for 2019
  qry = ' SELECT \n' \
        "    t1.*, " \
        "    LEFT(RIGHT(teaching_staff,7),6) AS emplid, " \
        "    LEFT(course_code,4) AS subject_area \n" \
        ' FROM {0}.{1} t1 \n' \
        " WHERE t1.teacher_count > 5 AND type IN ('Staff', 'Course') \n" \
        " ORDER BY t1.teaching_staff, t1.year, t1.semester, t1.type".format(schema, tbl)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


def get_teachers(cur, tbl='vw810_teacher_data_agg', schema='ces'):
  # Returns a data frame with change in CES data for 2019
  qry = ' SELECT \n' \
        "   LEFT(RIGHT(teaching_staff,7),6) AS emplid, teaching_staff, \n" \
        "   avg_gts, avg_crse_gts, avg_gts-avg_crse_gts AS avg_gts_diff \n" \
        ' FROM {0}.{1} \n' \
        ' WHERE count_2019 > 0 AND count >= 5 \n' \
        " ORDER BY avg_gts; \n" \
        "".format(schema, tbl)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)



'''-------------------------------------------- Set Parameters -------------------------------------'''
type_palette3 = sns.color_palette([rc.RMIT_Blue3, rc.RMIT_Orange3])

area_palette3 = sns.color_palette([rc.RMIT_Lemon3, rc.RMIT_Aqua3, rc.RMIT_Purple3, rc.RMIT_Green2])
area_palette2 = sns.color_palette([rc.RMIT_Lemon2, rc.RMIT_Aqua2, rc.RMIT_Purple2, rc.RMIT_Green2])
area_palette = sns.color_palette([rc.RMIT_Lemon, rc.RMIT_Aqua, rc.RMIT_Purple, rc.RMIT_Green])

type_palette2 = sns.color_palette([rc.RMIT_Blue2, rc.RMIT_Orange2])
type_palette = sns.color_palette([rc.RMIT_Blue, rc.RMIT_Orange])
step = 10
sns.set_style("darkgrid")
dims = (8.27, 11.69)
vert = False


x_val = 'gts'
y_val = 'emplid'

x_label = "Percent Agree"
y_label = "Employee ID"
legend_loc = 'lower left'

if not vert:
  temp = x_val
  x_val = y_val
  y_val = temp

  temp = x_label
  x_label = y_label
  y_label = temp
  dims = (11.69, 8.27)
  legend_loc = 'lower right'

'''-------------------------------------------- Create Dataframes -------------------------------------'''
df = get_course_teacher_ces(cur=postgres_cur, tbl='vw811_teacher_data', schema='ces')
df2 = get_teachers(cur=postgres_cur, tbl='vw810_teacher_data_agg', schema='ces')

df_school = df.loc[(df['school'] == 'EFM')]
teachers_school = df_school.loc[(df_school['year'] == 2019)]['emplid'].unique().tolist()


print(tabulate(df_school, headers='keys'))


df2_school = df2.loc[(df2['emplid'].isin(teachers_school))]

df2 = df2_school
df = df_school

j = 0
folder = 'H:\\Projects\\CoB\\CES\\Teachers\\'
for i in range(0, len(df2)+1, step):
  j += 1
  fig, ax = plt.subplots(figsize=dims)

  #print(tabulate(df2[i:i+step], headers='keys'))
  teachers = df2[i:i+step]['emplid'].tolist()

  sns.boxplot(x_val, y_val, ax=ax,
              data=df.loc[(df['emplid'].isin(teachers))],
              order=teachers,
              hue='type', hue_order=['Staff', 'Course'],
              palette=type_palette3,
              dodge=True,
              fliersize=0)

  sns.swarmplot(x_val, y_val, ax=ax,
                data=df.loc[(df['emplid'].isin(teachers)) & (df['type'] == 'Staff')],
                order=teachers,
                hue='subject_area', hue_order=['BAFI', 'ECON', 'MKTG', 'BUSM', '', '', '', ''],
                palette=area_palette3,
                edgecolor=rc.RMIT_Black, linewidth=0.5,
                dodge=True,
                size='gts_count')

  sns.swarmplot(x_val, y_val, ax=ax,
                data=df.loc[(df['emplid'].isin(teachers)) & (df['type'] == 'Course')],
                order=teachers,
                hue='type', hue_order=['', 'Course'],
                palette=type_palette2,
                edgecolor=rc.RMIT_Black, linewidth=0.5,
                size=5,
                dodge=True)
  
  sns.swarmplot(x_val, y_val, ax=ax,
                data=df.loc[(df['emplid'].isin(teachers) & (df['year'].isin([2019])) & (df['type'] == 'Staff'))],
                order=teachers,
                hue='subject_area', hue_order=['BAFI', 'ECON', 'MKTG', 'BUSM', '', '', '', ''],
                palette=area_palette,
                edgecolor=rc.RMIT_Black, linewidth=0.5,
                size=5,
                dodge=True)

  sns.swarmplot(x_val, y_val, ax=ax,
                data=df.loc[(df['emplid'].isin(teachers) & (df['year'].isin([2019])) & (df['type'] == 'Course'))],
                order=teachers,
                hue='type', hue_order=['', 'Course'],
                palette=type_palette,
                edgecolor=rc.RMIT_Black, linewidth=0.5,
                size=5,
                dodge=True)
  
  # Empty plot to fill in space in legend
  ax.plot(0, 0, '-', color='none', label='A')
  
  # Get the handles and labels.
  handles, labels = ax.get_legend_handles_labels()

  # When creating the legend,
  l = plt.legend(
    [handles[2], handles[7], handles[12], handles[0], handles[0],
     handles[1], handles[3], handles[4],  handles[5],  handles[6],
     handles[0], handles[8], handles[9], handles[10], handles[11]
     ],
    ['Course', 'Pre 2019', '2019', '', '',
     'Teacher', 'BAFI', 'ECON', 'MKTG', 'BUSM',
     '', 'BAFI 2019', 'ECON 2019', 'MKTG 2019', 'BUSM 2019'
     ],
    loc=legend_loc,
    ncol=3)
  #x = plt.xticks(rotation=30)

  ax.axes.set_title("Teacher/Course GTS comparison (2015-2019)", fontsize=16)
   
  ax.set_ylabel(y_label, fontsize=14)
   
  ax.set_xlabel(x_label, fontsize=14)
  
  if vert:
    ax.set_xlim([0, 105])
    plt.subplots_adjust(left=0.11, bottom=0.05, right=0.97, top=0.97)
    fig.savefig(folder + "EFM_teacher_gts_2019S1_vert_n{:02d}.png".format(j))
  else:
    ax.set_ylim([0, 105])
    plt.subplots_adjust(left=0.07, bottom=0.1, right=0.97, top=0.93)
    fig.savefig(folder + "EFM_teacher_gts_2019S1_hzon_n{:02d}.png".format(j))

  plt.close(fig)
