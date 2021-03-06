import base64
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from collections import OrderedDict
from tabulate import tabulate

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc

from Course_enhancement_graphs import (
  line_graph_measure_surveys,
  line_graph_program_measure_surveys,
  generate_ces_pd_table,
  line_graph_gtsq_surveys,
  generate_ces_pd_table,
  graphCourseProgramPie
)

from Course_enhancement_functions import (
  get_term_name,
  get_course_pop
)

from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
)


'''------------------------------ Helper functions -----------------------------------'''


def list_to_text(obList):
  # converts a list of object into a string list for sql IN statement
  txt = "("
  for ob in obList:
    txt += "'{}',".format(ob)
  txt = txt[:-1] + ")"
  return txt


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

def get_course_enhancement_list(year, semester, cur, tbl='vw100_courses', schema='course_enhancement'):
  # Returns a dataframe of the courses undergoing enhancement course in year, semester from db (cur)
  qry = " SELECT DISTINCT \n" \
        "   ce.level, ce.school_code, ce.course_code, \n" \
        "   ce.course_code_ces, \n" \
        "   ce.cluster_code, \n" \
        "   cd.school_name, cd.course_name \n" \
        " FROM ( \n" \
        "   SELECT level, school_code, course_code, course_code_ces, cluster_code  \n" \
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
        " WHERE course_code_ces IN {2} \n" \
        "	  AND year >= {3} \n" \
        "   AND year <= {4} \n" \
        " ORDER BY course_code_ces, year, semester; \n" \
        "".format(schema, tbl,
                  list_to_text(course_list),
                  start_year,
                  end_year)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)

def get_course_comments(course_list, year, semester, cur, tbl='vw202_course_comments', schema='ces'):
  # Returns a dataframe with CES comments for courses in course list from
  qry = """
  SELECT
  	CASE
      	WHEN pop.population <= 5 OR pop.population IS NULL THEN ''
      	ELSE comm.program_code END AS program_code,
  	best, improve, pop.course_code, pop.course_code_ces
  FROM (
    	SELECT course_code, course_code_ces, program_code, best, improve
    	FROM {0}.{1}
    	WHERE year = {2} AND semester = {3} AND course_code_ces IN {4}
  	) comm
  LEFT OUTER JOIN (
      SELECT
      	pc.course_code,
      	pc.course_code_ces,
        pc.program_code,
        pc.population
      FROM ces.vw115_course_program pc
      WHERE course_code_ces IN {4}
      	    AND year = {5}
      	    AND semester = {6}
  	) pop ON comm.program_code = pop.program_code AND comm.course_code_ces = pop.course_code_ces
  """.format(schema, tbl,
             year, semester,
             list_to_text(course_list),
             year, semester)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


def get_course_comments_themes(course_list, year, semester, cur, tbl='vw301_course_thematic', schema='ces'):
  ### Get micorsurgery course themes
  qry = " SELECT course_code, course_code_ces, themes \n" \
        " FROM  {0}.{1}\n" \
        " WHERE year = {2} AND semester = {3}  \n" \
        "     AND course_code_ces IN {4} \n" \
        "".format(schema, tbl,
                  year, semester,
                  list_to_text(course_list))
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)

def get_course_program_ces_data(course_list, start_year, end_year, cur, tbl='vw115_course_program', schema='ces'):
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
        "     course_code, cluster_code, course_code_ces, program_code, \n" \
        '     reliability, \n' \
        '     round(gts, 1) AS gts, round(gts_mean, 1) AS gts_mean, \n' \
        '     round(osi, 1) AS osi, round(osi_mean, 1) AS osi_mean, \n' \
        '     population::int, osi_count, gts_count \n' \
        '   FROM {0}.{1} \n' \
        "   WHERE course_code_ces IN {2} \n" \
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
        " ORDER BY course_code_ces, program_code, year, semester; \n" \
        "".format(schema, tbl,
                  list_to_text(course_list),
                  start_year,
                  end_year)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)


'''----------------------------- create dash functions -------------------------------------'''
def create_school_options(df_schools):
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
  
  options = [{'label': '{0}: {1}'.format(r['course_code_ces'],
                                         r['course_name']),
              'value': r['course_code_ces']} for i, r in f_df.sort_values(['course_code_ces']).iterrows()]
  options.insert(0, {'label': 'All', 'value': None})
  return options


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

def make_course_pack(course_code_ces,
                     df_ce,
                     df_ce_ces,
                     df_ce_comments,
                     df_ce_comment_themes,
                     df_ce_prg_ces,
                     logo,
                     ces_scale_image):
  # Main function that creates the Data pack for given course_code
  ## Note the first page header is not included as it forms part of the selection box
  
  # filters data frames to selected course
  df1_ce = get_course_data(df_ce, course_code_ces)
  df1_ces = get_course_data(df_ce_ces, course_code_ces)
  df1_comments = get_course_data(df_ce_comments, course_code_ces)
  df1_themes = get_course_data(df_ce_comment_themes, course_code_ces)
  df1_prg_ces = get_course_data(df_ce_prg_ces, course_code_ces)
  
  # get top 5 programs in most recent semester
  df1_enrl = df1_prg_ces.loc[(df1_prg_ces['year'] == end_year) &
                             (df1_prg_ces['semester'] == semester)]
  program_codes = df1_enrl.sort_values('population', ascending=False).head(n=5)['program_code'].tolist()
  program_codes = list(OrderedDict.fromkeys(program_codes))
  
  try:
    level = df1_ces['level'].tolist()[-1]
  except:
    level = 'HE'
  
  gts_list = get_gts_questions(level)
  
  # create themes text
  themes_txt = 'No themes identified.'  # Default themse text
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
                  figure=line_graph_measure_surveys(df1_ces, course_code_ces, ['gts', 'osi'], start_year, end_year,
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
                  figure=generate_ces_pd_table(df1_ces, course_code_ces),
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
                                                 course_code_ces,
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
        make_header_div(df1_ce, logo),
        # Second row - Student distribution Heading
        make_program_page(course_code_ces, df1_prg_ces, df1_enrl, program_codes),
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
                    ' The pie charts are based on {} Semester {} survey population.'
                    ''.format(end_year, semester))
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
                    ' The 5 largest program are determined using {} Semester {} survey population.'
                    ' These charts can help to determine how different cohorts view the course'
                    ''.format(end_year, semester))
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
                      'The **Qualitative Data** from the {} S{} CES is on the following pages.'
                      ''.format(comments_year, comments_semester))
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
              [dcc.Markdown('**Qualitative data ({} Semester {})**'
                            ''.format(comments_year, comments_semester))],
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


def make_header_div(df1, logo):
  # creates course header with pre defined logo
  course_code = df1['course_code_ces'].tolist()[0]
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


def make_header_div_selector(df_ce, df_schools, logo):
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
                    options=create_school_options(df_schools),
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




