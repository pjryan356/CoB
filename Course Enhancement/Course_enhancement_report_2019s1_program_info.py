import RMIT_colours as rc
import base64
import sys
import flask

sys.path.append('H:\\Data\\CoB Database\\pipeline\\')

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from Course_enhancement_graphs import (line_graph_measure_surveys,
                                       line_graph_program_measure_surveys,
                                       generate_ces_pd_table,
                                       line_graph_gtsq_surveys,
                                       generate_ces_pd_table,
                                       graphCourseProgramPie
                                       )
from Course_enhancement_functions import (get_term_name,
                                          get_course_pop,
                                          connect_to_postgres_db,
                                          db_extract_query_to_dataframe)

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
      school_code,
      course_code - ces course_code which includes clusters and vertical studios (-CL00),
      course_code_alt - regular course_code,
      school_name,
      course_name

  df_ce_ces (Original source - CES data summaries)
    contains the course level ces results for the past 5 years not all of the columns are used
      survey_year, survey_semester - of ces data
      survey_level - academic level [HE, VE] used to determine which GTS questions were asked
      course_code -
      reliability - [G (good), S (sufficient), N (insufficient)] based on survey_population and osi_response_count
      gts, gts_mean - gts percent agree [0-100] and mean gts [1-5]
      osi, osi_mean - osi percent agree [0-100] and mean osi [1-5]
      gts1, gts2, gts3, gts4, gts5, gts6 - percent agree for individual gts questions
      course_name
      course_coordinator
      survey_population
      osi_response_count
      gts_response_count
  
  df_ce_comments (Original source - file supplied by Student Surveys Team)
    contains the de-identified and censored CES comments for the courses
    comments are from the selected year and semester (most recent available (or equivalent) survey results)
      program_code - program code of student, '' if 5 or less students from the program were enrolled in the course
      best - answer to What was the best aspect of this course?
      improve - answer to What part of this course needs the most improvement?
      course_code
  
  df_ce_comment_themes (Original source - produced by CoB L&T team)
    contains the comment themes identified for the course by the L&T staff (from the selected year and semester)
      course_code
      themes
  
  df_ce_prg_enrl (Original source - SAMS database)
    contains some enrolment details for the course (not all columns are used)
    enrolments are the selected year and semester (current, previous or previous equivalent)
      term_code
      course_code
      program_code - Non CoB program codes are combined as 'Non CoB'
      population - student enrolments in course and program
      program_name -
      school_code - Non CoB school codes are listed as 'Non CoB'
      school_name - Non CoB school names are listed as 'Non CoB'
      school_name_short - Non CoB school names are listed as 'Non CoB'
      school_colour - each CoB school has been assigned a colour from the RMIT palette for consistency
      college - college SAMS code
      college_name - Full college names
      college_name_short - changes BUS to CoB
      college_colour - each college has been assigned a colour from the RMIT palette for consistency

  df_ce_prg_ces (Original source - file supplied by Student Surveys Team)
      year, semester - of ces data
      level - academic level [HE, VE] used to determine which GTS questions were asked
      course_code -
      program_code -
      reliability - [G (good), S (sufficient), N (insufficient)] based on survey_population and osi_response_count
      gts, gts_mean - gts percent agree [0-100] and mean gts [1-5]
      osi, osi_mean - osi percent agree [0-100] and mean osi [1-5]
      population
      osi_count
      gts_count
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
  end_year = 2018
  start_year = 2015
  
  year = 2019
  semester = 1
  
  enrl_year = 2018
  enrl_semester = 1
  
  comments_year = end_year
  comments_semester = 1

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
image_filename = 'C:\\Peter\\CoB\\logos\\CES_scale.png'  # replace with your own image
ces_scale_image = base64.b64encode(open(image_filename, 'rb').read())

'''------------------------------ Helper functions -----------------------------------'''


def get_last_semester(year, semester):
  # returns the previous year and semester based on a 2 semester year
  if semester != 1:
    semester -= 1
  else:
    semester = 2
    year -= 1
  return year, semester


def list_to_text(obList):
  # converts a list of object into a string list for sql IN statement
  txt = "("
  for ob in obList:
    txt += "'{}',".format(ob)
  txt = txt[:-1] + ")"
  return txt

def get_term_code_list(year, semester):
  # returns a list of major term code for a give year/semester
  termList = []
  st = int(year) - 2000
  if semester == 1:
    for end in ['05', '10', '20', '91']:
      termList.append('{}{}'.format(st, end))
  elif semester == 2:
    for end in ['45', '50', '60', '92']:
      termList.append('{}{}'.format(st, end))
  return termList


def get_gts_questions(level):
  # returns a list of the GTS questions for HE or VE
  if level == 'HE':
    gts_list = ['The teaching staff are extremely good at explaining things (SEi)',
                'The teaching staff normally give me helpful feedback on how I am going in this course (PE)',
                'The teaching staff motivate me to do my best work (SEi)',
                'The teaching staff work hard to make this course interesting (SEi)',
                'The teaching staff make a real effort to understand difficulties I might be having in this course (PE)',
                'The teaching staff put a lot of time into commenting on my work (PE)',
                '\*SEi: Student Engagement (impact);\u00A0\u00A0\*\*PE: Perceived Effort;']
  
  elif level == 'VE':
    gts_list = ['My instructors have a thorough knowledge of the course assessment (PC)',
                'My instructors provide opportunities to ask questions (SEp)',
                'My instructors treat me with respect (SEp)',
                'My instructors understand my learning needs (PC)',
                'My instructors communicate the course content effectively (SEi)',
                'My instructors make the course content as interesting as possible (SEi)',
                '\*PC: Perceived Capability;\u00A0\u00A0\*\*SEp: Student Engagement (practice);\u00A0\u00A0\*\*\*SEi: Student Engagement (impact);']
  else:
    gts_list = []
  
  return gts_list


def make_comments_rows(df1, empty_statement='No comments provided'):
  # creates a Dash table of comments from a panda data frame
  ## df should have 3 columns {program_code, best, improve}
  ## Empty df is empty: the empty_stement is placed in middle column
  ##    Postrges does not handle apostrophe and single quote marks well, they are often converted to a ?
  ##    hence all ? are converted to ', this is not perfect but creates less errors overall
  
  df1 = df1[['program_code', 'best', 'improve']]
  try:
    if len(df1) > 0:
      rows = [
        html.Tr(
          [html.Td(df1.iloc[i][col].replace("?", "'")) for col in df1.columns]
        ) for i in range(len(df1))
      ]
    else:
      rows = [html.Tr([html.Td(''), html.Td(empty_statement), html.Td('')])]
  except:
    rows = [html.Tr([html.Td(''), html.Td(empty_statement), html.Td('')])]
  return rows


'''----------------------------- create data extraction functions -------------------------------------'''


def get_course_enhancement_list(year, semester, cur, tbl, schema='course_enhancement'):
  # Returns a dataframe of the courses undergoing enhancement course in year, semester from db (cur)
  qry = " SELECT DISTINCT \n" \
        "   ce.level, ce.school_code, ce.course_code, SPLIT_PART(ce.course_code,'-', 1) AS course_code_alt, \n" \
        "   cd.school_name, cd.course_name \n" \
        " FROM ( \n" \
        "   SELECT level, school_code, course_code \n" \
        "	  FROM {0}.{1} \n" \
        "   WHERE year = {2} AND semester = {3} \n" \
        "       AND cob_selected IS NOT False \n" \
        "   ) ce \n" \
        " LEFT OUTER JOIN ( \n" \
        "   SELECT * FROM lookups.vw_course_details_recent \n" \
        "   ) cd ON (SPLIT_PART(cd.course_code,'-', 1) = SPLIT_PART(ce.course_code,'-', 1))\n" \
        " ORDER BY ce.school_code, ce.course_code \n" \
        "".format(schema, tbl,
                  year, semester)
  
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


def get_course_ces_data(course_list, start_year, end_year, cur, tbl, schema='ces_summaries'):
  # Returns a dataframe with CES data for courses in course list
  qry = ' SELECT \n' \
        "   survey_year, survey_semester, survey_level, SPLIT_PART(course_code,'-', 1) AS course_code, \n" \
        '   reliability, round(gts, 1) AS gts, round(gts_mean, 1) AS gts_mean, \n' \
        '   round(osi, 1) AS osi, round(osi_mean, 1) AS osi_mean, \n' \
        '   round(gts1, 1) AS gts1, round(gts2, 1) AS gts2, round(gts3, 1) AS gts3, \n' \
        '   round(gts4, 1) AS gts4, round(gts5, 1) AS gts5, round(gts6, 1) AS gts6, \n' \
        '   course_name, course_coordinator, survey_population, osi_response_count, gts_response_count \n' \
        ' FROM {0}.{1} \n' \
        " WHERE SPLIT_PART(course_code,'-', 1) IN {2} \n" \
        "	  AND survey_year >= '{3}' \n" \
        "   AND survey_year <= '{4}' \n" \
        "   AND all_flag = 'All' \n" \
        " ORDER BY course_code, survey_year, survey_semester; \n" \
        "".format(schema, tbl,
                  list_to_text(course_list),
                  start_year,
                  end_year)
  
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


def get_course_program_ces_data(course_list, start_year, end_year, cur, tbl, schema='ces'):
  # Returns a dataframe with CES data for courses in course list
  qry = ' SELECT \n' \
        "   year, semester, level,  \n" \
        "   course_code, program_code, \n" \
        '   reliability, \n' \
        '   round(gts, 1) AS gts, round(gts_mean, 1) AS gts_mean, \n' \
        '   round(osi, 1) AS osi, round(osi_mean, 1) AS osi_mean, \n' \
        '   population, osi_count, gts_count \n' \
        ' FROM {0}.{1} \n' \
        " WHERE SPLIT_PART(course_code,'-', 1) IN {2} \n" \
        "	  AND year >= {3} \n" \
        "   AND year <= {4} \n" \
        " ORDER BY course_code, program_code, year, semester; \n" \
        "".format(schema, tbl,
                  list_to_text(course_list),
                  start_year,
                  end_year)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


def get_course_comments(course_list, year, semester, cur, tbl, schema='ces'):
  # Returns a dataframe with CES comments for courses in course list from
  qry = """
  SELECT
  	CASE
      	WHEN prg.population <= 5 OR prg.population IS NULL THEN ''
      	ELSE comm.program_code END AS program_code,
  	best, improve, comm.course_code
  FROM (
    	SELECT course_code, program_code, best, improve
    	FROM {0}.{1}
    	WHERE year = {2} AND semester = {3} AND course_code IN {4}
  	) comm
  LEFT OUTER JOIN (
      SELECT
      	enrl.course_code,
        enrl.program_code,
        sum(enrl.population) AS population
      FROM enrolments.tbl_course_program_pop enrl
      WHERE enrl_status = 'E' AND enrl_reason = 'ENRL'
      	    AND course_code IN {4}
      	    AND term_code IN {5}
      GROUP BY enrl.course_code, enrl.program_code
  	) prg ON comm.program_code = prg.program_code AND comm.course_code = prg.course_code
  """.format(schema, tbl,
             year, semester,
             list_to_text(course_list),
             list_to_text(get_term_code_list(year, semester)))
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


def get_course_comments_themes(course_list, year, semester, cur, tbl, schema='course_enhancement'):
  ### Get micorsurgery course themes
  qry = " SELECT course_code, themes \n" \
        " FROM  {0}.{1}\n" \
        " WHERE year = {2} AND semester = {3}  \n" \
        "     AND SPLIT_PART(course_code,'-', 1) IN {4} \n" \
        "".format(schema, tbl,
                  year, semester,
                  list_to_text(course_list))
  
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


def get_course_prg_enrl(course_list, year, semester, cur, tbl, schema='enrolments'):
  ### Get microsurgery courses enrolments
  qry = " SELECT \n" \
        "	  enrl.term_code, enrl.course_code, \n" \
        "   CASE WHEN pd.college = 'BUS' THEN enrl.program_code ELSE 'Not CoB' END AS program_code, \n" \
        "   enrl.population, \n" \
        "   CASE WHEN pd.college = 'BUS' THEN pd.program_name ELSE 'Not CoB' END AS program_name, \n" \
        "   CASE WHEN pd.college = 'BUS' THEN pd.school_code ELSE 'Not CoB' END AS school_code, \n" \
        "   CASE WHEN pd.college = 'BUS' THEN pd.school_name ELSE 'Not CoB' END AS school_name, \n" \
        "   COALESCE(bsd.school_name_short, 'Not CoB') AS school_name_short, \n" \
        "   CASE WHEN pd.college = 'BUS' THEN bsd.html ELSE '#FAC800' END AS school_colour, \n" \
        "   pd.college, \n" \
        "   col.college_name, \n" \
        "   col.college_name_short, \n" \
        "   col.html AS college_colour \n " \
        " FROM ( \n" \
        "   SELECT term_code, course_code, program_code, population \n" \
        " 	FROM {0}.{1} \n" \
        " 	WHERE enrl_status = 'E' AND enrl_reason = 'ENRL' \n" \
        "     AND course_code IN {2} \n" \
        "     AND term_code IN {3} \n" \
        "  ) enrl \n" \
        " LEFT JOIN ( \n" \
        "   SELECT * \n" \
        "	  FROM lookups.tbl_program_details \n" \
        "   ) pd \n" \
        "   ON enrl.program_code = pd.program_code \n" \
        " LEFT JOIN ( \n" \
        "   SELECT sd.*, sc.html \n" \
        "  	FROM (SELECT * FROM lookups.tbl_bus_school_details) sd \n" \
        "   LEFT JOIN (SELECT * FROM lookups.tbl_rmit_colours) sc \n" \
        "     ON sc.colour_name = sd.colour \n" \
        "   ) bsd \n" \
        "   ON pd.school_code = bsd.school_code \n" \
        " LEFT JOIN ( \n" \
        "   SELECT cd.*, rc.html \n" \
        " 	FROM lookups.tbl_rmit_college_details cd, lookups.tbl_rmit_colours rc \n" \
        "   WHERE rc.colour_name = cd.colour \n" \
        "   ) col \n" \
        "   ON pd.college = col.college_code \n" \
        "".format(schema, tbl,
                  list_to_text(course_list),
                  list_to_text(get_term_code_list(year, semester)))
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


'''-------------------------------------------- Create Dataframes -------------------------------------'''
df_ce = get_course_enhancement_list(year, semester,
                                    cur=postgres_cur, tbl='tbl_courses', schema='course_enhancement')
df_schools = df_ce[['school_code', 'school_name']].drop_duplicates()
df_ce_ces = get_course_ces_data(df_ce['course_code_alt'].tolist(),
                                start_year,
                                end_year,
                                cur=postgres_cur, tbl='vw_summaries_combined', schema='ces_summaries')

df_ce_comments = get_course_comments(df_ce['course_code_alt'].tolist(),
                                     comments_year, comments_semester,
                                     cur=postgres_cur, tbl='vw_comments_censored_reduced', schema='ces')

df_ce_comment_themes = get_course_comments_themes(df_ce['course_code_alt'].tolist(),
                                                  comments_year, comments_semester,
                                                  cur=postgres_cur,
                                                  tbl='tbl_course_thematic', schema='course_enhancement')

df_ce_prg_enrl = get_course_prg_enrl(df_ce['course_code_alt'].tolist(),
                                     enrl_year, enrl_semester,
                                     cur=postgres_cur, tbl='tbl_course_program_pop', schema='enrolments')

df_ce_prg_ces = get_course_program_ces_data(df_ce['course_code_alt'].tolist(),
                                            start_year,
                                            end_year,
                                            cur=postgres_cur, tbl='vw4_course_program_combined', schema='ces')



'''----------------------------- create dash functions -------------------------------------'''
def create_school_options():
  # Create School options dropdown
  df_schools.sort_values(['school_name'])
  options = [{'label': '{1} ({0})'.format(r['school_code'],
                                          r['school_name']),
              'value': r['school_code']} for i, r in df_schools.iterrows()]
  options.insert(0, {'label': 'All', 'value': None})
  return options


def create_course_options(df1, school_code=None):
  # filters course list by given school code
  if school_code != None:
    f_df = df1.loc[df_ce['school_code'] == school_code]
  else:
    f_df = df1
  
  # Create Course options dropdown
  f_df.sort_values(['course_code'])
  options = [{'label': '{0}: {1}'.format(r['course_code'],
                                         r['course_name']),
              'value': r['course_code']} for i, r in f_df.iterrows()]
  options.insert(0, {'label': 'All', 'value': None})
  return options


def get_course_data(df1, course_code):
  # filters dataframe to given course_code
  try:
    return df1.loc[df1['course_code'] == course_code]
  except:
    return None

def make_program_page(course_code, df1_prg_ces, df1_enrol, term_code):
  # Function that creates the course Program Page for given course_code
  div = html.Div(
    [
      # Second row - Student distribution Heading
      html.Div(
        [
          html.P(
            [dcc.Markdown('**Student cohorts ({})** '
                          '\u00A0 Population: {}'.format(get_term_name(term_code),
                                                         get_course_pop(df1_enrol, term_code, course_code)))
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
                id='coll-pie-graph',
                figure=graphCourseProgramPie(df1_enrol, 'college'),
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
                id='prog-pie-graph',
                figure=graphCourseProgramPie(df1_enrol, 'program'),
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
                  course_code,
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
                  course_code,
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

def make_course_pack(course_code):
  # Main function that creates the Data pack for given course_code
  ## Note the first page header is not included as it forms part of the selection box
  
  # filters data frames to selected course
  df1_ce = get_course_data(df_ce, course_code)
  df1_ces = get_course_data(df_ce_ces, course_code)
  df1_comments = get_course_data(df_ce_comments, course_code)
  df1_themes = get_course_data(df_ce_comment_themes, course_code)
  df1_enrol = get_course_data(df_ce_prg_enrl, course_code)
  df1_prg_ces = get_course_data(df_ce_prg_ces, course_code)
  
  
  
  # get additional course parameters from data frames
  try:
    term_code = df1_enrol['term_code'].tolist()[-1]
  except:
    term_code = '1910'
  
  try:
    level = df1_ces['survey_level'].tolist()[-1]
  except:
    level = 'HE'
  
  gts_list = get_gts_questions(level)
  
  # create themes text
  themes_txt = 'No themes identified'  # Default themse text
  try:
    themes_txt = df1_themes.iloc[0].themes
  except:
    pass
  
  # create Data pack in correct layout
  child = [
    # First Page - CES quantitative data
    html.Div(
      [
        # First Row - OSI & GTS overtime graph and CES overtime table
        html.Div(
          [
            # OSI & GTS Graph
            html.Div(
              [
                dcc.Graph(
                  id='gts-graph',
                  figure=line_graph_measure_surveys(df1_ces, course_code, ['gts', 'osi'], start_year, end_year,
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
                  figure=generate_ces_pd_table(df1_ces, course_code),
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
        # Second Row - Individual GTS questions graph and CES questions list
        html.Div(
          [
            # Individual GTS questions overtime graph
            html.Div(
              [
                dcc.Graph(
                  id='gtsi-graph',
                  figure=line_graph_gtsq_surveys(df1_ces,
                                                 course_code,
                                                 start_year,
                                                 end_year, semester=None,
                                                 acad_career=level,
                                                 height=300),
                  style={'margin': 2,
                         },
                )
              ],
              className='six columns',
              style={'margin-left': 0,
                     'margin-right': 0},
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
              style={'margin-top': 20,
                     'margin-left': 0,
                     'margin-right': 0,
                     'margin-bottom': 0}
            ),
          ],
          className='twelve columns',
          style={'border': 'solid',
                 'margin-top': 5}
        )
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
    # Second Page - Program Distributions and CES data
    html.Div(
      [
        # First row - Page Header
        make_header_div(df1_ce),
        # Second row - Student distribution Heading
        make_program_page(course_code, df1_prg_ces, df1_enrol, term_code),
      ],
      style={'width': '29.4cm',
             'height': '19.9cm',
             'top-margin': 0,
             'bottom-margin': 0,
             'right-margin': 50,
             'left-margin': 50},
    ),
    html.Div([html.P('')],
             className='twelve columns',
             style={'bottom-margin': '50'},
             ),
  
    # Third Page - Additional Information
    html.Div(
      [
        # First row - Page Header
        make_header_div(df1_ce),
        # Second row - Heading
        html.Div(
          [
            html.P(
              children=[dcc.Markdown('**Additional Information**')],
              style={'fontSize': 24,
                     'margin-left': 20, })
          ],
          className='twelve columns',
          style={'text-align': 'left'},
        ),
        
        # Third row - Additional Information
        html.Div(
          className='row',
          style={'margin-bottom': 10,
                 'margin-top': 0,
                 'margin-left': 0,
                 'margin-right': 0, },
          children=[
            # GTS calculation explanation
            html.Div(
              className='six columns',
              style={'margin-bottom': 0,
                     'margin-top': 0,
                     'margin-left': 0,
                     'margin-right': 0, },
              children=
              [
                html.P(['How is the GTS score calculated?'],
                       style={'textAlign': 'center',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'bold',
                              'margin-bottom': 0,
                              'margin-top': 0,
                              'margin-left': 10,
                              'margin-right': 0},
                       ),
                html.P(['Each students can answer the OSI only once for the course.'],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 5,
                              'margin-left': 10},
                       ),
                html.P(['Each student has the option to answer the six GTS questions for every staff member in the course.'
                        ' Hence the total number of responses for the GTS is much higher than for the OSI.'],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 5,
                              'margin-left': 10},
                       ),
                html.P(['All CES questions are measured against a 5-point scale ranging from'
                        ' "Strongly Disagree" to "Strongly Agree".'],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 0,
                              'margin-left': 10},
                       ),
                html.Img(
                  src='data:image/png;base64,{}'.format(ces_scale_image.decode()),
                  style={'height': '80px',
                         'width': '520px',
                         'align': 'middle',
                         'vertical-align': 'middle',
                         'margin-top': 10,
                         'margin-bottom': 10,
                         'margin-left': 10,
                         'margin-right': 0,
                         }
                ),
                html.P(['The GTS percent agree is calculated by taking the sum of student responses that'
                        ' "Agree" or "Strongly Agree" with any GTS question for any teacher'
                        ' and expressing it as a percentage of all student GTS responses.'],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 5,
                              'margin-left': 10},
                       ),
                html.P(['In this methodology a neutral response ("Neither Agree or Disagree", 3) '
                        ' effectively counts as a did not agree.'],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 5,
                              'margin-left': 10,
                              },
                       ),
                html.P(['The GTS and OSI range from 0 to 100%.'],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 0,
                              'margin-left': 10,
                              },
                       ),
              ],
            ),
            # Chart explanations
            html.Div(
              className='six columns',
              style={'margin-bottom': 0,
                     'margin-top': 0,
                     'margin-left': 40,
                     'margin-right': 0, },
              children=
              [
                html.P(['Table & Chart information '],
                       style={'textAlign': 'center',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'bold',
                              'margin-bottom': 10,
                              'margin-top': 0,
                              'margin-left': 0,
                              'margin-right': 0},
                       ),
                html.P([dcc.Markdown(' The **reliability** (Rel) of the data in each survey is indicated by a letter:')],
                       style={'textAlign': 'left',
                              'font-size': 16,
                              'color': rc.RMIT_Black,
                              'font-weight': 'normal',
                              'margin-bottom': 0,
                              'margin-left': 20},
                       ),
                html.P([
                  '\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0G [Good]; S [Sufficient]; N [Insufficient]; or U [Unknown]'],
                  style={'textAlign': 'centered',
                         'font-size': 16,
                         'color': rc.RMIT_Black,
                         'font-weight': 'normal',
                         'margin-bottom': 20,
                         'margin-left': 20},
                ),
                # html.P([dcc.Markdown(' The **red line** indicates the school\'s GTS target for 2018')],
                #       style={'textAlign': 'left',
                #              'font-size': 16,
                #              'color': rc.RMIT_Black,
                #              'font-weight': 'normal',
                #              'margin-bottom': 0,
                #              'margin-left': 20
                #              },
                #       ),
                html.P(
                  [dcc.Markdown(
                    'The **pie charts** show what program, school and college the students in the course are from.'
                    ' Non CoB programs are grouped together.'
                    ' The pie charts are based on {} enrolments.'.format(get_term_name(term_code)))
                  ],
                  style={'textAlign': 'left',
                         'font-size': 16,
                         'color': rc.RMIT_Black,
                         'font-weight': 'normal',
                         'margin-bottom': 0,
                         'margin-left': 20
                         },
                ),
                html.P(
                  ['The 9 largest programs are shown.'
                   ' Any additional programs are included in Other (x).'
                   ' The number in brackets (x) represent how many individual programs are included in Other.'
                  ],
                  style={'textAlign': 'left',
                         'font-size': 16,
                         'color': rc.RMIT_Black,
                         'font-weight': 'normal',
                         'margin-bottom': 20,
                         'margin-left': 20
                        }
                ),
                html.P(
                  [dcc.Markdown(
                    'The **OSI and GTS Data by program** are graphed for the cohorts from the 5 largest programs.'
                    ' The 5 largest program are determined using {} enrolments.'
                    ' These charts can help to determine how different cohorts view the course'
                    ''.format(get_term_name(term_code)))
                  ],
                  style={'textAlign': 'left',
                         'font-size': 16,
                         'color': rc.RMIT_Black,
                         'font-weight': 'normal',
                         'margin-bottom': 20,
                         'margin-left': 20
                         },
                ),
                html.P(
                    [dcc.Markdown(
                      'The **Qualitative Data** from the {} CES is on the following pages.'
                      ''.format(get_term_name(term_code, short=True)))
                    ],
                    style={'textAlign': 'left',
                           'font-size': 16,
                           'color': rc.RMIT_Black,
                           'font-weight': 'normal',
                           'margin-bottom': 0,
                           'margin-left': 20
                           },
                ),
                html.P(
                  [dcc.Markdown(
                    'The **Themes Identified** are a summation of the main themes from the student comments.'
                    ' The full list of student comments from the course are also provided.')
                  ],
                  style={'textAlign': 'left',
                         'font-size': 16,
                         'color': rc.RMIT_Black,
                         'font-weight': 'normal',
                         'margin-bottom': 0,
                         'margin-left': 20
                         },
                ),
              ],
            ),
          ],
        ),
      ],
      style={'width': '29.4cm',
             'height': '19.9cm',
             'top-margin': 0,
             'bottom-margin': 0,
             'right-margin': 50,
             'left-margin': 50},
    ),
    html.Div([html.P('')],
             className='twelve columns',
             style={'bottom-margin': '50'},
             ),
    html.Div([html.P('')],
             className='twelve columns',
             style={'bottom-margin': '50'},
             ),
    html.Div([html.P('')],
             className='twelve columns',
             style={'bottom-margin': '50'},
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
              [dcc.Markdown('**Qualitative data ({})**'.format(get_term_name(term_code)))],
              style={'fontSize': 24,
                     'margin-left': 20, })
          ],
          className='twelve columns',
          style={'text-align': 'left'},
        ),
        # Third row - Comment Themes
        html.Div(
          children=[
            # Heading
            html.P(
              [dcc.Markdown('Themes Identified')],
              style={'textAlign': 'center',
                     'font-size': 20,
                     'color': rc.RMIT_Black,
                     'font-weight': 'bold',
                     'text-decoration': 'underline',
                     'margin-top': 0,
                     'margin-bottom': 0,
                     'margin-left': 20,
                     'margin-right': 20},
            ),
            # Themes text
            html.P(
              id='theme_comments',
              children=[dcc.Markdown('{}'.format(themes_txt))],
              style={'textAlign': 'center',
                     'font-size': 18,
                     'color': rc.RMIT_Black,
                     'font-weight': 'normal',
                     'margin-top': 0,
                     'margin-bottom': 0,
                     'margin-left': 20,
                     'margin-right': 20},
            )
          ],
          className='twelve columns',
          style={
            'border': 'solid',
            'border-color': '{}'.format(rc.RMIT_Green),
            'border-width': '10pt',
            'margin-bottom': 20},
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
                      [html.Th('Program', style={'width': 80, 'text-align': 'center'}),
                       html.Th('What was the best aspect of this course?', style={'width': 560}),
                       html.Th('What part of this course needs the most improvement?', style={'width': 560}),
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
  ]
  return child


def make_header_div(df1):
  # creates course header with pre defined logo
  course_code = df1['course_code'].tolist()[0]
  course_name = df1['course_name'].tolist()[0]
  school_name = df1['school_name'].tolist()[0]
  
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
def update_course_dropdown(school_code):
  return create_course_options(df_ce, school_code)


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
  app.run_server(port=8050, host='127.0.0.1', debug=True)
