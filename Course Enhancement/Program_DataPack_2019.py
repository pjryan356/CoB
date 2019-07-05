## Program CES Data Pack
# Peter Ryan Feb 2019

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from tabulate import tabulate

import general.RMIT_colours as rc
from general.sams_helper_functions import (return_sams_engine)
from general.sams_queries import (
  qry_program_course_structure
)

from general.postgres_queries import (
  qry_course_enhancement_list
)

from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
)


'''
This script is designed to a Program level CES Data Pack.
  Get the program structure from the SAMS database
 '''


'''------------------------------------- Get Inputs  --------------------------------'''
# Set parameter values with input prompts or go with preset values (input prompt)
# Get Program Code
#program_code = input("Program Code: ") ## Input password
program_code = 'AD010'

# Setup app
app = dash.Dash(__name__)
app.scripts.config.serve_locally = True

''' ------------------- Add a css file to configure settings and layouts-------------'''
# The main css file used was copied from https://codepen.io/chriddyp/pen/bWLwgP.css
# When used 'directly' it had an undo/redo button located in bottom left corner of every page
# This was 'fixed' by appending the 'remove_undo.css' file
# In order to work the css files had to appended using the methodology outlined at
#   https://community.plot.ly/t/how-do-i-use-dash-to-add-local-css/4914/2
##  I do not fully understand how this works and sometimes it messes up

# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"}) # direct css usage



'''--------------------------------- Connect to Database  ----------------------------'''
# create sams engine this is the connection to the oracle database
password_str = input("SAMS Password: ") ## Input password
sams_engine = return_sams_engine(password_str=password_str)

'''
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
'''



'''-------------------------------------------- Create Dataframes -------------------------------------'''

# get program structure from sams
sams_qry = qry_program_course_structure(program_code=program_code)
try:
  df_prg_crse = pd.read_sql(sql=sams_qry, con=sams_engine)
except:
  print(sams_qry)

print(tabulate(df_prg_crse, headers='keys'))


df_prg = df_prg_crse[['program_code', 'plan_code', 'effdt', 'program_name', 'program_level', 'school_abbr', 'campus']].drop_duplicates(['program_code', 'plan_code'])

for i, prg in df_prg.iterrows():
  print(prg)
  df_crses = df_prg_crse.loc[df_prg_crse['plan_code'] == prg['plan_code']][['ams_block_nbr', 'clist_name', 'crse_id', 'course_code', 'course_name']]
  print(tabulate(df_crses, headers='keys'))


def get_course_data(df1, course_code_ces):
  # filters dataframe to given course_code
  try:
    return df1.loc[df1['course_code_ces'] == course_code_ces]
  except:
    try: df1.loc[df1['course_code'] == course_code_ces]
    except:
      pass
  return None

def make_program_page(course_code_ces, df1_prg_ces, df1_enrol, program_codes):
  # Function that creates the course Program Page for given course_code
  div = html.Div(
    [
      # Second row - Student distribution Heading
      html.Div(
        [
          html.P(
            [dcc.Markdown('**Student cohorts ({} Semester {})** '
                          '\u00A0 Population: {}'
                          ''.format(end_year, semester,
                                    get_course_pop(df1_enrol, course_code_ces,
                                                   year=end_year,
                                                   semester=semester)))
             ],
            style={'fontSize': 24,
                   'margin-left': 20, })
        ],
        className='twelve columns',
        style={'text-align': 'left'},
      ),
      # Third Row - Student distribution Pie Charts
      html.Div(
        children=[
          html.Div(  # Pie - Program
            [
              dcc.Graph(
                id='prg-pie-graph',
                figure=graphCourseProgramPie(df1_enrol, 'program'),
                style={'border': 'solid'},
              )
            ],
            className='four columns',
          ),
          html.Div(  # Pie - School
            [
              dcc.Graph(
                id='sch-pie-graph',
                figure=graphCourseProgramPie(df1_enrol, 'school'),
                style={'border': 'solid'},
              )
            ],
            className='four columns',
          ),
          html.Div(  # Pie - College
            [
              dcc.Graph(
                id='col-pie-graph',
                figure=graphCourseProgramPie(df1_enrol, 'college'),
                style={'border': 'solid'},
              )
            ],
            className='four columns',
          ),
        ],
        className='twelve columns',
        style={'margin-bottom': 10}
      ),
      # Fourth row - Program CES charts
      html.Div(
        className='row',
        style={'margin-bottom': 10,
               'margin-top': 0,
               'margin-left': 0,
               'margin-right': 0, },
        children=[
          html.Div(  # OSI - Program
            [
              dcc.Graph(
                id='prg-osi-graph',
                figure=line_graph_program_measure_surveys(
                  df1_prg_ces,
                  course_code_ces,
                  program_codes,
                  measure='osi',
                  start_year=start_year,
                  end_year=end_year, semester=None,
                  width=520, height=320),
                style={'border': 'solid'},
              )
            ],
            className='six columns',
          ),
          html.Div(  # GTS - Program
            [
              dcc.Graph(
                id='prg-gts-graph',
                figure=line_graph_program_measure_surveys(
                  df1_prg_ces,
                  course_code_ces,
                  program_codes,
                  measure='gts',
                  start_year=start_year,
                  end_year=end_year, semester=None,
                  width=520, height=320),
                style={'border': 'solid'},
              )
            ],
            className='six columns',
          ),
        ],
      ),
    ],
  )
  return div

