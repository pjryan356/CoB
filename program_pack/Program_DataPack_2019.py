## Program CES Data Pack
# Peter Ryan Feb 2019
import base64
import flask
import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from collections import OrderedDict
from tabulate import tabulate

from IPython.core.interactiveshell import InteractiveShell

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

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

from Course_enhancement_graphs import (
  line_graph_measure_surveys,
  line_graph_gtsq_surveys,
  line_graph_crse_prg,
  generate_ces_pd_table,
  )

from Course_enhancement_functions import (
  get_term_name,
  get_course_pop,
  get_gts_questions
)

'''
This script is designed to a Program level CES Data Pack.
  Get the program structure from the SAMS database
 '''


'''------------------------------------- Get Inputs  --------------------------------'''
# Set parameter values with input prompts or go with preset values (input prompt)
# Get Program Code
#program_code = input("Program Code: ") ## Input password
program_code_test = 'BP253'
start_year = 2016
end_year = 2019
semester = 2

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

'''------------------------Get Images---------------------'''
# header image
image_filename = 'C:\\Peter\\CoB\\logos\\L&T_Transparent_200.png'  # replace with your own image
logo = base64.b64encode(open(image_filename, 'rb').read())

# ces scale image (3 explanation)
image_filename = 'C:\\Peter\\CoB\\logos\\CES_scale2.png'  # replace with your own image
ces_scale_image = base64.b64encode(open(image_filename, 'rb').read())




'''------------------------------ Helper functions -----------------------------------'''
def list_to_text(obList):
  # converts a list of object into a string list for sql IN statement
  txt = "("
  for ob in obList:
    txt += "'{}',".format(ob)
  txt = txt[:-1] + ")"
  return txt

def get_courses_data(df1, course_list):
  # filters dataframe to given course_code
  try:
    return df1.loc[df1['course_code'].isin(course_list)]
  except:
      pass
  return None

def get_program_data(df1, code, plan=None):
  # filters dataframe to given course_code
  try:
    return df1.loc[df1['program_code'] == code]
  except:
    pass
  return None

'''----------------------------- create data extraction functions -------------------------------------'''
def get_course_enhancement_list(year, semester, cur, schema='course_enhancement'):
  # Returns a dataframe of the courses undergoing enhancement course in year, semester from db (cur)
  qry = qry_course_enhancement_list(year, semester, 'vw100_courses', schema)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


def get_course_ces_data(course_list, start_year, end_year, cur, tbl='vw1_course_summaries_fixed', schema='ces'):
  # Returns a dataframe with CES data for courses in course list
  qry = ' SELECT \n' \
        "   year, semester, level, \n" \
        "   course_code, \n" \
        "   course_code_ces, \n" \
        '   reliability, round(gts, 1) AS gts, round(gts_mean, 1) AS gts_mean, \n' \
        '   round(osi, 1) AS osi, round(osi_mean, 1) AS osi_mean, \n' \
        '   round(gts1, 1) AS gts1, round(gts2, 1) AS gts2, round(gts3, 1) AS gts3, \n' \
        '   round(gts4, 1) AS gts4, round(gts5, 1) AS gts5, round(gts6, 1) AS gts6, \n' \
        '   course_coordinator, population, osi_count, gts_count \n' \
        ' FROM {0}.{1} \n' \
        " WHERE course_code IN {2} \n" \
        "	  AND year >= {3} \n" \
        "   AND year <= {4} \n" \
        " ORDER BY course_code, year, semester; \n" \
        "".format(schema, tbl,
                  list_to_text(course_list),
                  start_year,
                  end_year)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)

def get_course_program_ces_data(course_list, program_list, start_year, end_year, cur, tbl='vw115_course_program', schema='ces'):
  # Returns a dataframe with CES data for courses in course list
  qry = ' SELECT \n' \
        '   crse_prg.*, \n' \
        '   pd.program_name, \n' \
        "   CASE WHEN pd.college = 'BUS' THEN pd.school_code ELSE 'Not CoB' END AS school_code, \n" \
        "   COALESCE(bsd.school_name_short, 'Not CoB') AS school_name_short, \n" \
        "   CASE WHEN pd.college = 'BUS' THEN bsd.html ELSE '#FAC800' END AS school_colour, \n" \
        "   pd.college, \n" \
        "   col.college_name_short, \n" \
        "   col.html AS college_colour \n " \
        ' FROM ( \n' \
        '   SELECT \n' \
        "     year, semester, level,  \n" \
        "     course_code, course_code_ces, program_code, \n" \
        '     reliability, \n' \
        '     round(gts, 1) AS gts, round(gts_mean, 1) AS gts_mean, \n' \
        '     round(osi, 1) AS osi, round(osi_mean, 1) AS osi_mean, \n' \
        '     population::int, osi_count, gts_count \n' \
        '   FROM {0}.{1} \n' \
        "   WHERE course_code IN {2} \n" \
        "     AND year >= {3} \n" \
        "     AND year <= {4} \n" \
        "   ) crse_prg \n" \
        " LEFT JOIN ( \n" \
        "   SELECT program_code, program_name, school_code, college \n" \
        "   FROM lookups.tbl_program_details \n" \
        "   ) pd ON (crse_prg.program_code = pd.program_code) \n" \
        " LEFT JOIN ( \n" \
        "   SELECT sd.school_code, sd.school_name_short, sc.html \n" \
        "   FROM (SELECT  school_code, school_name_short, colour FROM lookups.tbl_bus_school_details) sd \n" \
        "   LEFT JOIN (SELECT colour_name, html FROM lookups.tbl_rmit_colours) sc \n" \
        "     ON sc.colour_name = sd.colour \n" \
        "   ) bsd ON (pd.school_code=bsd.school_code)\n" \
        " LEFT JOIN ( \n" \
        "   SELECT cd.college_code, cd.college_name, cd.college_name_short, rc.html \n" \
        " 	FROM lookups.tbl_rmit_college_details cd, lookups.tbl_rmit_colours rc \n" \
        "   WHERE rc.colour_name = cd.colour \n" \
        "   ) col ON (pd.college = col.college_code) \n" \
        " WHERE crse_prg.program_code IN {5} \n" \
        " ORDER BY course_code, year, semester; \n" \
        "".format(schema, tbl,
                  list_to_text(course_list),
                  start_year,
                  end_year,
                  list_to_text(program_list))
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)

def get_prg_ces_data(program_list, start_year, end_year, cur, tbl='vw135_program', schema='ces'):
  # Returns a dataframe with CES data for courses in course list
  qry = ' SELECT \n' \
        "   year, semester, level, \n" \
        "   program_code, \n" \
        '   population::int, reliability, \n' \
        '   round(gts::numeric, 1) AS gts, round(gts_mean::numeric, 1) AS gts_mean, \n' \
        '   round(osi::numeric, 1) AS osi, round(osi_mean::numeric, 1) AS osi_mean, \n' \
        '   round(gts1::numeric, 1) AS gts1, round(gts2::numeric, 1) AS gts2, round(gts3::numeric, 1) AS gts3, \n' \
        '   round(gts4::numeric, 1) AS gts4, round(gts5::numeric, 1) AS gts5, round(gts6::numeric, 1) AS gts6 \n' \
        ' FROM {0}.{1} \n' \
        " WHERE program_code IN {2} \n" \
        "	  AND year >= {3} \n" \
        "   AND year <= {4} \n" \
        " ORDER BY year, semester; \n" \
        "".format(schema, tbl,
                  list_to_text(program_list),
                  start_year,
                  end_year)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


def get_prg_crse_data(program_list, cur):
  qry = " SELECT * \n" \
        " FROM programs.tbl_plan_course_structure \n" \
        " WHERE program_code IN {} " \
        "".format(list_to_text(program_list))
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)

'''-------------------------------------------- Create Dataframes -------------------------------------'''

df_prg_crse = get_prg_crse_data([program_code_test], cur=postgres_cur)

df_prg = df_prg_crse[['program_code', 'plan_code', 'program_name', 'program_level', 'school_abbr', 'campus']].drop_duplicates(['program_code', 'plan_code', 'campus', 'program_name', 'school_abr', 'program_level', 'school_abbr', 'campus'])
df_prg = df_prg.loc[df_prg['campus'] == 'AUSCY']

df_schools = df_prg[['school_abbr']].drop_duplicates()

df_crses = df_prg_crse[['course_code', 'course_name', 'ams_block_nbr', 'clist_name']].drop_duplicates()

df_crse_prg_ces = get_course_program_ces_data(df_crses['course_code'].tolist(),
                                              df_prg['program_code'].tolist(),
                                              start_year,
                                              end_year,
                                              cur=postgres_cur)

df_prg_ces = get_prg_ces_data(df_prg['program_code'].tolist(),
                              start_year,
                              end_year,
                              cur=postgres_cur)

df_crse_ces = get_course_ces_data(df_crses['course_code'].tolist(),
                                  start_year,
                                  end_year,
                                  cur=postgres_cur)

df_crses_year = df_crses.loc[(df_crses['ams_block_nbr'] == 1)]



'''----------------------------- create dash functions -------------------------------------'''
def create_school_options():
  # Create School options dropdown
  df_schools.sort_values(['school_abbr'])
  options = [{'label': '{0}'.format(r['school_abbr']),
              'value': r['school_abbr']} for i, r in df_schools.iterrows()]
  options.insert(0, {'label': 'All', 'value': None})
  return options

def create_program_options(df1, school=None):
  # filters course list by given school code
  if school != None:
    f_df = df1.loc[df1['school_abbr'] == school]
  else:
    f_df = df1
  
  # Create Program options dropdown
  
  options = [{'label': '{0}: {1}'.format(r['program_code'],
                                         r['program_name']),
              'value': r['program_code']} for i, r in f_df.sort_values(['program_code']).iterrows()]
  options.insert(0, {'label': 'All', 'value': None})
  return options


def make_program_level_page(program_code, level, df1_prg_ces, gts_list):
  # First Page - CES quantitative data
  div = html.Div(
    [
      # First Row - OSI & GTS overtime graph and CES overtime table
      html.Div(
        [
          # OSI & GTS Graph
          html.Div(
            [
              dcc.Graph(
                id='gts-graph',
                figure=line_graph_measure_surveys(
                  df1_prg_ces,
                  program_code,
                  ['gts', 'osi'],
                  start_year, end_year,
                  semester=None,
                  width=540,
                  height=320
                ),
                style={'margin': 0,
                       },
              )
            ],
            className='six columns',
            style={
              'width': '50%',
              'margin-left': 0,
              'margin-right': 0,
            }
          ),
          # CES Table
          html.Div(
            children=[
              dcc.Graph(
                id='ces-table',
                figure=generate_ces_pd_table(df1_prg_ces,
                                             program_code,
                                             width=530,
                                             height=310),
                style={
                  'margin': 0,
                  'margin-top': 5,
                  'margin-bottom': 5,
                  'margin-left': 10,
                  'margin-right': 10,
                },
              )
            ],
            className='six columns',
            style={
              'width': '50%',
              'margin': 0,
              'margin-left': 0,
              'margin-right': 0,
            },
          ),
        ],
        className='row',
        style={
               'border': 'solid',
               'margin-top': 5,
        },
      ),
      # Second Row - Individual GTS questions graph and CES questions list
      html.Div(
        [
          # Individual GTS questions overtime graph
          html.Div(
            [
              dcc.Graph(
                id='gtsi-graph',
                figure=line_graph_gtsq_surveys(
                  df1_prg_ces,
                  program_code,
                  start_year,
                  end_year, semester=None,
                  acad_career=level,
                  width=530,
                  height=320),
                style={'margin': 0,
                       },
              )
            ],
            className='six columns',
            style={'width': '50%',
                   'margin': 0,
                   'margin-right': 0
                   },
          ),
          # CES question explanations
          html.Div(
            [
              html.P(['GTS Questions'],
                     style={'margin': 0,
                            'font-weight': 'bold'}),
              html.P(['Q1: {}'.format(gts_list[0])], style={'margin': '0'}),
              html.P(['Q2: {}'.format(gts_list[1])], style={'margin': '0'}),
              html.P(['Q3: {}'.format(gts_list[2])], style={'margin': '0'}),
              html.P(['Q4: {}'.format(gts_list[3])], style={'margin': '0'}),
              html.P(['Q5: {}'.format(gts_list[4])], style={'margin': '0'}),
              html.P(['Q6: {}'.format(gts_list[5])], style={'margin': '0'}),
              html.P([dcc.Markdown('{}'.format(gts_list[6]))],
                     style={'margin-top': '5'}),
              html.P([dcc.Markdown('**OSI:** {}'.format('Overall I am satisfied with the quality of this course'))],
                     style={'margin-top': '5'}),
      
            ],
            className='six columns',
            style={'width': '50%',
                   'margin-top': 10,
                   'margin-left': 0,
                   'margin-right': 0,
                   'margin-bottom': 0}
          ),
        ],
        className='row',
        style={'border': 'solid',
               'margin-top': 5}
      )
    ],
    className='row',
    style={'width': '29.5cm',
           'height': '18.6 cm',
           'margin-left': 0,
           'margin-right': 0,
           'margin-bottom': 0,
           'margin-top': 0,
           }
  )
  return div

def make_course_div(course_code):
  # Side by side GTS & OSI graphs
  div = html.Div(
    [
      # GTS Graph
      html.Div(
        [
          dcc.Graph(
            id='gts-graph-{}'.format(course_code),
            figure=line_graph_crse_prg(
              df_prg_ces,
              df_crse_ces,
              df_crse_prg_ces,
              df_crses,
              course_code,
              'gts',
              start_year, end_year,
              semester=None,
              width=545,
              height=320),
            style={'margin': 0},
          )
        ],
        className='six columns',
        style={'width': '50%',
               'margin': 0
               }
      ),
      # OSI Graph
      html.Div(
        [
          dcc.Graph(
            id='osi-graph-{}'.format(course_code),
            figure=line_graph_crse_prg(
              df_prg_ces,
              df_crse_ces,
              df_crse_prg_ces,
              df_crses,
              course_code,
              'osi',
              start_year, end_year,
              semester=None,
              width=545,
              height=320),
            style={'margin': 0},
          )
        ],
        className='six columns',
        style={'width': '50%',
               'margin': 0
               }
      ),
    ],
    className='row',
    style={'border': 'solid',
           }
  )
  return div

def make_program_year_level_page(program_code, year_level):
  # First Page - CES quantitative data
  prg = df_prg.loc[(df_prg['program_code'] == program_code)].reset_index(drop=True)
  df_crses_year = df_crses.loc[(df_crses['ams_block_nbr'] == year_level)].reset_index(drop=True)

  crse_list = df_crses_year['course_code'].drop_duplicates().tolist()
  
  # Course CES quantitative data
  sub_div = []
  for i_crse in range(0, len(crse_list), 2):
    try:
      crse = df_crses_year.loc[df_crses_year['course_code'] == crse_list[i_crse]]
    except:
      raise
    
    if i_crse + 1 < len(crse_list):
      try:
        temp = \
          html.Div(
              [
                make_year_header_div(prg, crse['clist_name'].tolist()[0]),
                make_course_div(crse_list[i_crse]),
                make_course_div(crse_list[i_crse+1]),
              ],
              style={'width': '29.5cm',
                     'height': '20.4cm',
                     'top-margin': 0,
                     'bottom-margin': 0,
                     'right-margin': 50,
                     'left-margin': 50,
                     }
              )
        sub_div.append(temp)
        
      except Exception as e:
        print(e, e.args)
        pass

    else:
      try:
        temp = \
          html.Div(
            [
              make_year_header_div(prg, crse['clist_name'].tolist()[0]),
              make_course_div(crse_list[i_crse]),
            ],
            style={'width': '29.5cm',
                   'height': '20.5cm',
                   'top-margin': 0,
                   'bottom-margin': 0,
                   'right-margin': 50,
                   'left-margin': 50,
                   'backgroundColor': rc.RMIT_Blue
                   }
          )
        sub_div.append(temp)
      
      except Exception as e:
        print(e.message, e.args)
        pass
      
  return html.Div(children=sub_div)

def make_program_pack(program_code):
  # Main function that creates the Data pack for given course_code
  ## Note the first page header is not included as it forms part of the selection box
  
  # filters data frames to selected course
  df1_crse_prg_ces = get_program_data(df_crse_prg_ces, program_code)
  df1_prg_ces = get_program_data(df_prg_ces, program_code)
  df1_prg_crse = get_program_data(df_prg_crse, program_code)
  
  try:
    level = df1_prg_ces['level'].tolist()[-1]
  except:
    level = 'HE'
  
  gts_list = get_gts_questions(level)
  
  # Create year level pages
  year_list = []
  for year in df1_prg_crse['ams_block_nbr'].drop_duplicates().tolist():
    year_list.append(make_program_year_level_page(program_code, year))
  
  
  # create Data pack in correct layout
  child = [
    # First Page - CES quantitative data
    make_program_level_page(program_code, level, df1_prg_ces, gts_list),
  
    # Second Page - Additional Information
    html.Div(
      children=make_addtional_info(),
      style={'width': '29.5cm',
             'height': '20.5cm',
             'top-margin': 0,
             'bottom-margin': 0,
             'right-margin': 50,
             'left-margin': 50,
             },
    ),
    # Add Year Level Pages - CES data
    html.Div(children=year_list),
    
    

  ]
  return child

def make_addtional_info():
  child = [
        # Heading (one column)
        html.Div(
          [
            html.P(
              children=[dcc.Markdown('**Additional Information**')],
              style={'fontSize': 24}
            )
          ],
          className='twelve columns',
          style={'text-align': 'center'},
        ),
        
        # Information (two columns)
        html.Div(
          className='twelve columns',
          style={'margin': 0,
                 },
          children=[
            # GTS calculation explanation
            html.Div(
              className='six columns',
              style={'width': '50%',
                     'margin': 0,
                     },
              children=[
                html.P(['How is the GTS (& OSI) Percent Agree calculated?'],
                       style={'textAlign': 'center',
                              'font-size': 18,
                              'color': rc.RMIT_Black,
                              'font-weight': 'bold',
                              'margin-bottom': 0,
                              'margin-top': 0,
                              'margin-left': 10,
                              'margin-right': 10},
                       ),
                html.P(['Each students can answer the OSI only once for a course.'],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 5,
                              'margin-left': 10,
                              'margin-right': 10,
                              },
                       ),
                html.P(
                  ['Each student has the option to answer the six GTS questions for every staff member in a course.'
                   ' Hence the number of GST responses can be much higher the number of OSI responses.'],
                  style={'textAlign': 'left',
                         'font-size': 16,
                         'color': rc.RMIT_Black,
                         'font-weight': 'normal',
                         'margin-bottom': 5,
                         'margin-left': 10,
                         'margin-right': 10,
                         },
                  ),
                html.P(['The OSI and GTS questions are measured against a 5-point scale ("1: Strongly Disagree to '
                        '"5: Strongly Agree").'],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 0,
                              'margin-left': 10,
                              'margin-right': 10,
                              },
                       ),

                html.P(['The GTS percent agree is calculated by taking the sum of student responses that'
                        ' "4: Agree" or "5: Strongly Agree" and expressing it as a percentage of all GTS responses.'],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 5,
                              'margin-left': 10,
                              'margin-right': 10,
                              },
                       ),
                html.P(['This means that a neutral response ("3: Neither Agree or Disagree") '
                        ' is effectively counted as a did not agree.'],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 5,
                              'margin-left': 10,
                              'margin-right': 10,
                              },
                       ),
                html.Img(
                  src='data:image/png;base64,{}'.format(ces_scale_image.decode()),
                  style={'height': '120px',
                         'width': '400px',
                         'align': 'middle',
                         'vertical-align': 'middle',
                         'margin-top': 10,
                         'margin-bottom': 10,
                         'margin-left': 60,
                         'margin-right': 0,
                         }
                ),
                html.P(['The GTS and OSI range from 0 to 100%.'],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 0,
                              'margin-left': 10,
                              'margin-right': 10,
                              },
                       ),
              ],
            ),
            # Chart explanations
            html.Div(
              className='six columns',
              style={'width': '50%',
                     'margin-bottom': 0,
                     'margin-top': 0,
                     'margin-left': 0,
                     'margin-right': 0,
                     },
              children=[
                html.Div(
                  style={
                         'margin-bottom': 0,
                         'margin-top': 0,
                         'margin-left': 10,
                         'margin-right': 10,
                         },
                  children=[
                    html.P(['Course Plots'],
                         style={'textAlign': 'center',
                                'font-size': 18,
                                'color': rc.RMIT_Black,
                                'font-weight': 'bold',
                                'margin-bottom': 0,
                                'margin-top': 0,
                                'margin-left': 0,
                                'margin-right': 0},
                         ),
                    html.P(
                      [dcc.Markdown('The following pages contain plots for every Course listed in the Program structure,'
                                    ' with GTS plots on the left and OSI plots on the right.')],
                      style={'textAlign': 'left',
                             'font-size': 16,
                             'color': rc.RMIT_Black,
                             'font-weight': 'normal',
                             'margin-bottom': 0,
                             'margin-left': 0},
                    ),
                    html.P(
                      [dcc.Markdown('The Course/Program scores (Red) are calculated using all student responses'
                                    ' for the Course, from students enrolled in the Program. The number of student'
                                    ' responses is displayed.')],
                      style={'textAlign': 'left',
                             'font-size': 16,
                             'color': rc.RMIT_Black,
                             'font-weight': 'normal',
                             'margin-bottom': 5,
                             'margin-left': 0},
                    ),
                    
                    html.P(
                      [dcc.Markdown('The Course scores (Dark Blue) are calculated using all student responses'
                                    ' for the Course, regardless of the Program.')],
                      style={'textAlign': 'left',
                             'font-size': 16,
                             'color': rc.RMIT_Black,
                             'font-weight': 'normal',
                             'margin-bottom': 0,
                             'margin-left': 0},
                    ),
                    html.P(
                      [dcc.Markdown(
                        'Compared the Course/Program and the Course lines to see how your students rate'
                        ' this Course compared to other students enrolled in the Course.'
                        ''.format(end_year, semester))
                      ],
                      style={'textAlign': 'left',
                             'font-size': 16,
                             'color': rc.RMIT_Black,
                             'font-weight': 'normal',
                             'margin-bottom': 10,
                             'margin-left': 0
                             },
                    ),
                    html.P(
                      [dcc.Markdown('The Program scores (Blue) are calculated using all responses,'
                                    ' regardless of the Course, from any student enrolled in the Program.'
                                    ' This information is the same as display in the Program plots on Page One')],
                      style={'textAlign': 'left',
                             'font-size': 16,
                             'color': rc.RMIT_Black,
                             'font-weight': 'normal',
                             'margin-bottom': 0,
                             'margin-left': 0},
                    ),
                    html.P(
                      [dcc.Markdown(
                        'Compared the Course/Program and the Program lines to see how your students rate'
                        ' this Course compared to the rest of the Program.'
                        ''.format(end_year, semester))
                      ],
                      style={'textAlign': 'left',
                             'font-size': 16,
                             'color': rc.RMIT_Black,
                             'font-weight': 'normal',
                             'margin-bottom': 0,
                             'margin-left': 0
                             },
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ]
  return child
  
def make_year_header_div(prg, list_name):
  # creates course header with pre defined logo
  try:
    code = prg.iloc[0]['program_code']
    name = prg.iloc[0]['program_name']
    school = prg.iloc[0]['school_abbr']
    div = html.Div(
      [
        # Left - Headings
        html.Div(
          [
            # Heading
            html.Div(
              children='Program Pack',
              style={'textAlign': 'left',
                     'font-size': 18,
                     'color': rc.RMIT_Black,
                     'font-weight': 'bold',
                     'padding-left': '10px',
                     },
            ),
            # Sub Heading
            html.Div(
              [
                html.P(
                  children='{}: {}'.format(code, name),
                  style={'textAlign': 'left',
                         'font-size': 16,
                         'color': rc.RMIT_Black,
                         'font-weight': 'bold',
                         'margin-bottom': 0,
                         'padding-left': '20px',
                         },
                ),
                html.P(
                  children='{}'.format(list_name),
                  style={'textAlign': 'left',
                         'font-size': 16,
                         'color': rc.RMIT_Black,
                         'font-weight': 'bold',
                         'margin-bottom': 0,
                         'padding-left': '30px',
                         },
                ),
              ],
            ),
          ],
          className='six columns',
          style={'width': '50%',
                 'top-margin': 0,
                 'bottom-margin': 0,
                 'right-margin': 0,
                 'left-margin': 0,
                 }
        ),
        # Right - Legend
        html.Div(
          [
            html.P(
              children=['Course (Program): Students enrolled in the Course and Program'],
              style={'textAlign': 'left',
                     'padding-left': '10px',
                     'font-size': 18,
                     'color': rc.RMIT_White,
                     'font-weight': 'normal',
                     'margin-top': 1,
                     'margin-bottom': 2,
                     'margin-left': 0,
                     'right-margin': 0,
                     'background-color': rc.RMIT_Red},
            ),

            html.P(
              children=['Course: Students enrolled in the Course, from any Program'],
              style={'textAlign': 'left',
                     'padding-left': '10px',
                     'font-size': 18,
                     'color': rc.RMIT_White,
                     'font-weight': 'normal',
                     'margin-top': 0,
                     'margin-bottom': 1,
                     'margin-left': 0,
                     'right-margin': 0,
                     'background-color': rc.RMIT_DarkBlue},
            ),
            html.P(
              children=['Program: Students enrolled in the Program, from any Course'],
              style={'textAlign': 'left',
                     'padding-left': '10px',
                     'font-size': 18,
                     'color': rc.RMIT_White,
                     'font-weight': 'normal',
                     'margin-top': 2,
                     'margin-bottom': 2,
                     'margin-left': 0,
                     'right-margin': 0,
                     'background-color': rc.RMIT_Blue},
            ),
          ],
          className='six columns',
          style={
            'width': '50%',
            'top-margin': 0,
            'bottom-margin': 0,
            'margin-right': 0,
            'margin-left': 0,
          },
        ),
      ],
      className='twelve columns',
      style={'border': 'solid',
             }
    )
  except:
    div = html.Div(
      [],
      className='twelve columns',
      style={'border': 'solid'}
    )
  
  return div

def make_header_div_selector():
  # Creates first header with course and school dropdown menus
  div = html.Div(
    className='twelve columns',
    style={'width': '29.5cm',
           'border': 'solid',
           'top-margin': 0,
           'bottom-margin': 0,
           'right-margin': 0,
           'left-margin': 0},
    children=
    [
      # Left - Dropdown menus
      html.Div(
        className='six columns',
        style={'width': '50%'},
        children=[
          # Heading
          html.Div(
            children='Program Pack',
            style={
              'textAlign': 'left',
              'font-size': 18,
              'color': rc.RMIT_Black,
              'font-weight': 'bold',
              'padding-left': '10px',
            },
          ),
          html.Div(
            style={
              'font-size': 14,
              'color': rc.RMIT_Black,
              'font-weight': 'bold',
              'top-margin': 0,
              'bottom-margin': 0,
              'right-margin': 0
            },
            children=[
              dcc.Dropdown(
                id='program-dropdown',
                options=create_program_options(df_prg),
                value=None,
                placeholder="Select a Program",
              ),
            ],
          ),
          html.Div(
            style={'font-size': 14,
                   'color': rc.RMIT_Black,
                   'font-weight': 'bold',
                   'top-margin': 0,
                   'bottom-margin': 0,
                   'right-margin': 0,
                   },
            children=[
              dcc.Dropdown(
                id='school-dropdown',
                options=create_school_options(),
                value=None,
                placeholder="Select a School"
              ),
            ],
          ),
        ],
      ),
      # Right - Image
      html.Div(
        className='five columns',
        style={
          'width': '45%',
          'align': 'middle',
          'vertical-align': 'middle',
          'top-margin': 0,
          'bottom-margin': 0,
          'right-margin': 0,
          'left-margin': 0,
          },
        children=[
          html.Img(
            src='data:image/png;base64,{}'.format(logo.decode()),
            style={'height': '80px',
                   'align': 'middle',
                   'vertical-align': 'middle',
                   'margin-top': 10,
                   'margin-left': 180}
          ),
        ],
      ),
    ],
  )
  return div

# Create app layout
app.layout = html.Div(
  [
    make_header_div_selector(),
    html.Div(
      id='program-pack'
    ),
  ]
)

'''----------------------- Main Graph Controlled ----------------------------------'''
'''---------------------- Options updates -----------------------------'''
''' Dropdowns'''

# Update course options based on school selection
@app.callback(Output('program-dropdown', 'options'),
              [Input('school-dropdown', 'value')])
def update_course_dropdown(school):
  return create_program_options(df_prg, school)


# Update the data pack based on program selection
@app.callback(
  Output('program-pack', 'children'),
  [Input('program-dropdown', 'value')],
)
def create_page(program_code):
  if program_code is None:
    return []
  else:
    return make_program_pack(program_code)


# Upload css formats
css_directory = 'H:\\Data\\CoB Database\\pipeline\\static\\'
stylesheets = ['bWLwgP.css', 'remove_undo.css']

@app.server.route('/<stylesheet>')
def serve_stylesheet(stylesheet):
  if stylesheet not in stylesheets:
    raise Exception('"{}" is excluded from the allowed static files'.format(stylesheet))
  return flask.send_from_directory(css_directory, stylesheet)


for stylesheet in stylesheets:
  app.css.append_css({"external_url": "{}".format(stylesheet)})

if __name__ == '__main__':
  app.run_server(port=8050, host='127.0.0.2', debug=False)