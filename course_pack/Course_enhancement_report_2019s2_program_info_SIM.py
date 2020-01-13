import base64
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from collections import OrderedDict
from tabulate import tabulate

from IPython.core.interactiveshell import InteractiveShell

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc

from Course_enhancement_graphs_SIM import (
  generate_sim_ces_pd_table,
  sim_line_graph_measure_surveys
)

'''
This script is designed to produce the Course Enhancement Data Packs.
  On running it produces a weblink with two dropdown menus
  The School and Course need to be selected to display the data pack
  The Data Pack is then printed as a PDF (save with school and course_code)

The data is sourced from a local database which pre processes the data into the desired format
The data is pulled into 4 pandas dataframes
  df_ce (Original source - internal CoB documents)
    contains the course details of the courses undergoing course enhancement
    it is mainly used to produce the drop down menus and the queries for other dataframes
      level - academic level [HE, VE]
      school_code, - 4 character code (e.g. 650T = Vocational Businesss Eduction)
      course_code, - 8-9 character code
      course_code_ces, - ces course_code which includes clusters and vertical studios (e.g. -CL00)
      cluster_code, - This is redundant information
      school_name, - Full school name
      course_name - Full course name

  df_ce_ces (Original source - CES data summaries)
    contains the course level ces results for the past 5 years not all of the columns are used
      year, semester - of ces data
      level - academic level [HE, VE] used to determine which GTS questions were asked
      course_code - 8-9 character code
      course_code_ces, - ces course_code which includes clusters and vertical studios (e.g. -CL00)
      reliability - [G (good), S (sufficient), N (insufficient)] based on population and osi_count
      gts, gts_mean - gts percent agree [0-100] and mean gts [1-5]
      osi, osi_mean - osi percent agree [0-100] and mean osi [1-5]
      gts1, gts2, gts3, gts4, gts5, gts6 - percent agree for individual gts questions
      course_coordinator - not used
      population - total survey population
      osi_count - number of students who responded to survey from the population
      gts_count - not used
  
  df_ce_comments (Original source - file supplied by Student Surveys Team)
    contains the de-identified and censored CES comments for the courses
    comments are from the selected year and semester (most recent available (or equivalent) survey results)
      program_code - 5 character program code of student, '' if 5 or less students from the program were enrolled in the course
      best - answer to What was the best aspect of this course?
      improve - answer to What part of this course needs the most improvement?
      course_code - as above
      course_code_ces - as above
'''

'''------------------------------------- Get Inputs  --------------------------------'''
# Set parameter values with input prompts or go with preset values (input prompt)
## It asks for prompts twice I am not sure why


set_values = input("Do you want to manually input the semester/term variables [Y/N]: ")
if set_values == 'Y':
  end_year = input("Last year of CES data (Current): ")
  start_year = input("First year of CES data (Recommend -4 years): ")
  
  year = input("Year of Course Enhancement: ")
  semester = input("Semester of Course Enhancement: ")
  
  enrl_year = input("Year of demographics (Current or -1): ")
  enrl_semester = input("Semester of demographics (Current): ")
  
  comments_year = end_year
  comments_semester = input("Semester of comments (Current): ")
else:
  end_year = 2019
  start_year = 2017
  
  year = 2019
  semester = 2
  
  enrl_year = 2019
  enrl_semester = 2
  

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

'''------------------------Get Images---------------------'''
# header image
image_filename = 'C:\\Peter\\CoB\\logos\\L&T_Transparent_200.png'  # replace with your own image
logo = base64.b64encode(open(image_filename, 'rb').read())

# ces scale image (3 explanation)
image_filename = 'C:\\Peter\\CoB\\logos\\CES_scale.png'  # replace with your own image
ces_scale_image = base64.b64encode(open(image_filename, 'rb').read())


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


def make_comments_rows(df1, empty_statement='No comments provided'):
  # creates a Dash table of comments from a panda data frame
  ## df should have 3 columns {program_code, best, improve}
  ## Empty df is empty: the empty_stement is placed in middle column
  ##    Postrges does not handle apostrophe and single quote marks well, they are often converted to a ?
  ##    hence all ? are converted to ', this is not perfect but creates less errors overall
  df1 = df1[['year', 'semester', 'staff_type', 'comment_type', 'comment_text']]
  print(tabulate(df1, headers='keys'))
  #print(len(df1))
  #print(tabulate(df1, headers='keys'))
  try:
    if len(df1) > 0:
      rows = [
        html.Tr(
          [html.Td(df1.iloc[i][col]) for col in df1.columns]
        ) for i in range(len(df1))
      ]
      #print(rows)
    else:
      rows = [html.Tr([html.Td(''), html.Td(''), html.Td(''), html.Td(''), html.Td(empty_statement)])]
  except:
    raise
    
    rows = [html.Tr([html.Td(''), html.Td(empty_statement), html.Td('')])]
  return rows


'''----------------------------- create data extraction functions -------------------------------------'''
def get_sim_course_list(year, semester, cur, tbl='vw100_course', schema='sim_ces'):
  # Returns a dataframe of the courses in SIM in year, semester from db (cur)
  qry = ' SELECT DISTINCT \n' \
        '   school, course_code, course_name \n ' \
        ' FROM {0}.{1} \n' \
        "	WHERE year = {2} \n" \
        "   AND semester = {3} \n" \
        " ORDER BY school, course_code; \n" \
        "".format(schema, tbl,
                  year,
                  semester)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


def get_course_sim_ces_data(course_list, start_year, end_year, cur, tbl='vw100_course', schema='sim_ces'):
  # Returns a dataframe with SIM CES data for courses in course list
  qry = ' SELECT \n' \
        '   year, semester, school, course_code, course_name, staff_type, ' \
        '   responses, population, \n' \
        '   round(subject_content,2) AS subject_content, \n' \
        '   round(lecturer_effectiveness,2) AS lecturer_effectiveness, \n' \
        '   round(course_satisfaction,2) AS course_satisfaction \n ' \
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

def get_sim_course_comments(course_list, year, semester, cur, tbl='vw001_course_teacher_comments', schema='sim_ces'):
  # Returns a dataframe with CES comments for courses in course list from
  qry = """
    SELECT year, semester, course_code, staff_type, student_load, comment_type, comment_text
    FROM {0}.{1}
    WHERE length(comment_text) > 4
          AND course_code IN {2}
    ORDER BY course_code, year, semester, staff_type, comment_type
  """.format(schema, tbl,
             list_to_text(course_list))
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


'''-------------------------------------------- Create Dataframes -------------------------------------'''
df_ce = get_sim_course_list(year, semester,
                            cur=postgres_cur)

#print(tabulate(df_ce, headers='keys'))

df_schools = df_ce[['school']].drop_duplicates()
df_ce_ces = get_course_sim_ces_data(df_ce['course_code'].tolist(),
                                    start_year,
                                    end_year,
                                    cur=postgres_cur)

txt = ''
for i, r in df_ce_ces.iterrows():
  if r['course_code'] not in txt:
    txt += "'{}', \n".format(r['course_code'])

print(txt)

#print(tabulate(df_ce_ces[:10], headers='keys'))
df_ce_comments = get_sim_course_comments(df_ce['course_code'].tolist(),
                                         year, semester,
                                         cur=postgres_cur)

#for measure in ['subject_content', 'lecturer_effectiveness', 'course_satisfaction']:
# print(min(df_ce_ces[measure]), max(df_ce_ces[measure]))

#print(tabulate(df_ce_comments, headers='keys'))


'''----------------------------- create dash functions -------------------------------------'''
def create_school_options():
  # Create School options dropdown
  df_schools.sort_values(['school'])
  options = [{'label': '{0}'.format(r['school']),
              'value': r['school']} for i, r in df_schools.iterrows()]
  options.insert(0, {'label': 'All', 'value': None})
  return options


def create_course_options(df1, school_code=None):
  # filters course list by given school code
  if school_code != None:
    f_df = df1.loc[df_ce['school'] == school_code]
  else:
    f_df = df1

  # Create Course options dropdown
  options = [{'label': '{0}: {1}'.format(r['course_code'],
                                         r['course_name']),
              'value': r['course_code']} for i, r in f_df.sort_values(['course_code']).iterrows()]
  options.insert(0, {'label': 'All', 'value': None})
  return options

def get_sim_course_data(df1, course_code):
  # filters dataframe to given course_code
  try:
    return df1.loc[df1['course_code'] == course_code]
  except:
    pass
  return None

def make_program_page(course_code_ces, df1_enrol):
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
    ],
  )
  return div

def make_course_pack(course_code):
  # Main function that creates the Data pack for given course_code
  ## Note the first page header is not included as it forms part of the selection box
  
  # filters data frames to selected course
  df1_ce = get_sim_course_data(df_ce, course_code)
  df1_ces = get_sim_course_data(df_ce_ces, course_code)
  df1_comments = get_sim_course_data(df_ce_comments, course_code)
  
  #print(tabulate(df1_comments, headers='keys'))
  
  '''
  # get top 5 programs in most recent semester
  df1_enrl = df1_prg_ces.loc[(df1_prg_ces['year'] == end_year) &
                             (df1_prg_ces['semester'] == semester)]
  program_codes = df1_enrl.sort_values('population', ascending=False).head(n=5)['program_code'].tolist()
  program_codes = list(OrderedDict.fromkeys(program_codes))
  '''

  # create Data pack in correct layout
  child = [
    # First Page - CES quantitative data
    html.Div(
      [
        # First Row - Subject Content overtime graph and CES overtime table
        html.Div(
          [
            # Subject Content Graph
            html.Div(
              [
                dcc.Graph(
                  id='sc-graph',
                  figure=sim_line_graph_measure_surveys(df1_ces, course_code,
                                                        ['subject_content'],
                                                         start_year, end_year,
                                                         semester=None),
                  style={'margin': 2},
                )
              ],
              className='six columns',
              style={'margin-left': 0,
                     'margin-right': 0, }
            ),
            # CES Table
            html.Div(
              children=[
                dcc.Graph(
                  id='ces-table',
                  figure=generate_sim_ces_pd_table(df1_ces, course_code),
                  style={'margin': 0,
                         'margin-top': 0,
                         'margin-left': 0,
                         'margin-right': 0,
                         },
                )
              ],
              className='six columns',
              style={'margin': 0,
                     'margin-left': 0,
                     'margin-right': 0,
                     }
            ),
          ],
          className='twelve columns',
          style={'border': 'solid',
                 'margin-top': 5}
        ),
        # Second Row - Lecturer Effectiveness & Course Satisfaction overtime graph
        html.Div(
          [
            # Lecturer Effectiveness Graph
            html.Div(
              [
                dcc.Graph(
                  id='le-graph',
                  figure=sim_line_graph_measure_surveys(df1_ces, course_code,
                                                        ['lecturer_effectiveness'],
                                                        start_year, end_year,
                                                        semester=None),
                  style={'margin': 2},
                )
              ],
              className='six columns',
              style={'margin-left': 0,
                     'margin-right': 0, }
            ),
            # Course Satisfaction Graph
            html.Div(
              children=[
                dcc.Graph(
                  id='cs-graph',
                  figure=sim_line_graph_measure_surveys(df1_ces, course_code,
                                                        ['course_satisfaction'],
                                                        start_year, end_year,
                                                        semester=None),
                  style={'margin': 0,
                         'margin-top': 0,
                         'margin-left': 0,
                         'margin-right': 0,
                         },
                )
              ],
              className='six columns',
              style={'margin': 0,
                     'margin-left': 0,
                     'margin-right': 0,
                     }
            ),
          ],
          className='twelve columns',
          style={'border': 'solid',
                 'margin-top': 5}
        ),
      ],
      style={'width': '29.4cm',
             'height': '20.25cm',
             'top-margin': 0,
             'bottom-margin': 20,
             'right-margin': 50,
             'left-margin': 50}
    ),
    html.Div([html.P('')],
             className='twelve columns',
             style={'bottom-margin': 50},
             ),
    
    # Third page - Qualitative CES data
    ## Depending on the number of pages this will expanded to any number of pages
    html.Div(
      [
        # First row - Page Header
        make_header_div(df1_ce),
        # Second row - Heading
        html.Div(
          [
            html.P(
              [dcc.Markdown('**Qualitative data**')],
              style={'fontSize': 24,
                     'margin-left': 20, })
          ],
          className='twelve columns',
          style={'text-align': 'left'},
        ),
        # Fourth row - Comments table
        html.Div(
          [
            # Table
            html.Div(
              [
                html.Table(
                  # Header
                  [
                    html.Tr(
                      [html.Th('Year', style={'width': 20, 'text-align': 'center'}),
                       html.Th('Sem', style={'width': 10, 'text-align': 'center'}),
                       html.Th('Staff', style={'width': 25, 'text-align': 'center'}),
                       html.Th('Comment area', style={'width': 80, 'text-align': 'center'}),
                       html.Th('Comment', style={'width': 560}),
                       ],
                      style={'border': 'solid',
                             }
                    )
                  ] +
                
                  # Body
                  make_comments_rows(df1_comments),
                  style={'border': 'solid',
                         'alignment': 'centre',
                         },
                )
              ],
              className='twelve columns',
              style={'text-align': 'center'},
            ),
          ],
          className='twelve columns',
          style={'margin-bottom': 10}
        ),
      ],
      style={'width': '29.4cm',
             'height': '19.9cm',
             'top-margin': 0,
             'bottom-margin': 20,
             'right-margin': 25,
             'left-margin': 25, }
    ),
    html.Div([html.P('')],
             className='twelve columns',
             style={'bottom-margin': 50},
             ),
  ]
  return child


def make_header_div(df1):
  # creates course header with pre defined logo
  try:
    course_code = df1['course_code'].tolist()[0]
    course_name = df1['course_name'].tolist()[0]
    school_name = df1['school'].tolist()[0]
    div = html.Div(
      [
        # Left - Headings
        html.Div(
          [
            # Heading
            html.Div(
              children='Course Pack',
              style={'textAlign': 'left',
                     'font-size': 18,
                     'color': rc.RMIT_Black,
                     'font-weight': 'bold',
                     'margin-left': 2
                     },
            ),
            # Sub Heading
            html.Div(
              [
                html.P(
                  children='{}: {}'.format(course_code, course_name),
                  style={'textAlign': 'left',
                         'font-size': 16,
                         'color': rc.RMIT_Black,
                         'font-weight': 'bold',
                         'margin-bottom': 0,
                         'margin-left': 2
                         },
                ),
                html.P(
                  children='{}'.format(school_name),
                  style={'textAlign': 'left',
                         'font-size': 16,
                         'color': rc.RMIT_Black,
                         'font-weight': 'bold',
                         'margin-left': 10,
                         'margin-top': 0},
                ),
              ],
            ),
          ],
          className='seven columns'
        ),
        # Right - Image (logo)
        html.Div(
          [
            html.Img(
              src='data:image/png;base64,{}'.format(logo.decode()),
              style={'height': '80px',
                     'align': 'middle',
                     'vertical-align': 'middle',
                     'margin-top': 2}
            ),
          ],
          className='five columns',
          style={'align': 'middle',
                 'vertical-align': 'middle'
                 }
        ),
      ],
      className='twelve columns',
      style={'border': 'solid'}
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
    [
      # Left - Dropdown menus
      html.Div(
        [
          # Heading
          html.Div(
            children='Course Pack',
            style={'textAlign': 'left',
                   'font-size': 18,
                   'color': rc.RMIT_Black,
                   'font-weight': 'bold',
                   'margin-left': 2
                   },
          ),
          # Dropdowns
          html.Div(
            [
              html.Div(
                [
                  dcc.Dropdown(
                    id='course-dropdown',
                    options=create_course_options(df_ce),
                    value=None,
                    placeholder="Select a Course",
                  ),
                ],
                className='ten columns',
                style={'font-size': 14,
                       'color': rc.RMIT_Black,
                       'font-weight': 'bold',
                       'border': 'None'}
              ),
              html.Div(
                [
                  dcc.Dropdown(
                    id='school-dropdown',
                    options=create_school_options(),
                    value=None,
                    placeholder="Select a School"
                  ),
                ],
                className='ten columns',
                style={'font-size': 14,
                       'color': rc.RMIT_Black,
                       'font-weight': 'bold'}
              ),
            ],
          ),
        ],
        className='seven columns'
      ),
      # Right - Image
      html.Div(
        [
          html.Img(
            src='data:image/png;base64,{}'.format(logo.decode()),
            style={'height': '80px',
                   'align': 'middle',
                   'vertical-align': 'middle',
                   'margin-top': 2}
          ),
        ],
        className='five columns',
        style={'align': 'middle',
               'vertical-align': 'middle'
               }
      ),
    ],
    className='twelve columns',
    style={'border': 'solid',
           'width': '29.4cm',
           'top-margin': 0,
           'bottom-margin': 0,
           'right-margin': 50,
           'left-margin': 50},
  )
  return div


# Create app layout
app.layout = html.Div(
  [
    make_header_div_selector(),
    html.Div(
      id='course-pack'
    ),
  ]
)

'''----------------------- Main Graph Controlled ----------------------------------'''
'''---------------------- Options updates -----------------------------'''
''' Dropdowns'''

# Update course options based on school selection
@app.callback(Output('course-dropdown', 'options'),
              [Input('school-dropdown', 'value')])
def update_course_dropdown(school):
  return create_course_options(df_ce, school)


# Update the data pack based on course selection
@app.callback(
  Output('course-pack', 'children'),
  [Input('course-dropdown', 'value')],
)
def create_page(course_code):
  return make_course_pack(course_code)


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
  app.run_server(port=8050, host='127.0.0.1', debug=False)
