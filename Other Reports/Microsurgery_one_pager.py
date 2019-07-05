

import plotly.graph_objs as go

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

from tabulate import tabulate

import dash
import dash_core_components as dcc
import dash_html_components as html

import base64

import general.RMIT_colours as rc
from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
)



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
con, cur = connect_to_postgres_db(con_string)

'''--------------------------------- Initialise Parameters  ----------------------------'''
term_code = '1810'


'''------------------------Get Images---------------------'''
# header image
image_filename = 'C:\\Peter\\CoB\\logos\\L&T_Transparent_200.png'  # replace with your own image
logo = base64.b64encode(open(image_filename, 'rb').read())


def get_avg_course_improve(cur, measure='gts', decimal_places=2,
                           schema='ces_summaries',
                           table='microsurgery_2018_sem1_benchmarks_all'):
  qry = ' SELECT \n' \
        '   avg({0}_2016_2017_m) AS measure_bm, \n' \
        '   avg({0}_2018_m) AS measure_2018 \n' \
        ' FROM {1}.{2}\n' \
        ' WHERE {0}_2018_n > 0 \n;' \
        ''.format(measure, schema, table)
  df = db_extract_query_to_dataframe(qry, cur)
  return [round(df.iloc[0]['measure_bm'], decimal_places), round(df.iloc[0]['measure_2018'], decimal_places)]


def get_course_improve():
  qry = ' SELECT survey_level, course_code, \n' \
        '   round(gts_2016_2017_m, 2) AS gts_bm, \n' \
        '   round(gts_2018_m, 2) AS gts_2018, \n' \
        '   round(gts_2018_m-gts_2016_2017_m, 2) AS gts_diff, \n' \
        '   round(osi_2016_2017_m, 2) AS osi_bm, \n' \
        '   round(osi_2018_m, 2) AS osi_2018, \n' \
        '   round(osi_2018_m-gts_2016_2017_m, 2) AS osi_diff \n' \
        ' FROM ces_summaries.microsurgery_2018_sem1_benchmarks_all \n' \
        ' WHERE gts_2018_n > 0; \n'
  df = db_extract_query_to_dataframe(qry, cur)
  return df


def get_school_targets_improve(year, decimal_places=0):
  qry = ' SELECT \n' \
        '   ROUND(100.0*sum(better_than_target)/sum(total), {0}) AS better \n' \
        '	FROM ces_summaries.microsurgery_2018_sem1_school_targets_counts \n' \
        " WHERE acad_year = '{1}' \n" \
        ''.format(decimal_places, year)
  df = db_extract_query_to_dataframe(qry, cur)
  return df.iloc[0]['better']

df_courses = get_course_improve()

def create_course_improve_bar(x, y, width, height):
  bar_colours = []
  for val in y:
    if val <= 0:
      bar_colours.append(rc.RMIT_Red)
    else:
      bar_colours.append(rc.RMIT_Green)
  
  bar = go.Bar(
    x=y,
    y=x,
    orientation='h',
    text=None,
    textposition='outside',
    marker=dict(color=bar_colours,
                line=dict(color=bar_colours)),
  )
  
  layout = go.Layout(
    paper_bgcolor=rc.RMIT_DarkBlue,
    plot_bgcolor=rc.RMIT_DarkBlue,
    title=None,
    showlegend=False,
    xaxis=dict(
      showgrid=True,
      zeroline=True,
      showticklabels=True,
      gridcolor=rc.RMIT_White,
      zerolinecolor=rc.RMIT_White,
      tickfont=dict(
        size=14,
        color=rc.RMIT_White
      )
    ),
    yaxis=dict(
      tickvals=None,
      showgrid=False,
      showticklabels=False,
      ticks='',
      zeroline=True,
      zerolinecolor=rc.RMIT_White),
    width=width,
    height=height,
    margin=dict(b=20, l=10, r=10, t=10),
    hidesources=True,
  )
  return go.Figure(data=[bar], layout=layout)


def create_improve_bar(x, y, width, height, maxy=90):
  bar = go.Bar(
    x=x,
    y=y,
    text=y,
    textposition='outside',
    marker=dict(
      color=[rc.RMIT_DarkBlue, rc.RMIT_Green]),
  )
  
  layout = go.Layout(
    title=None,
    showlegend=False,
    xaxis=dict(
      tickvals=None,
      showgrid=False,
      ticktext=None,
      showticklabels=False,
      ticks='',
      zeroline=False),
    yaxis=dict(
      range=[0, maxy],
      tickvals=None,
      showgrid=False,
      showticklabels=False,
      ticks='',
      zeroline=False),
    width=width,
    height=height,
    margin=dict(b=0, l=10, r=0, t=10),
    hidesources=True,
  )
  return go.Figure(data=[bar], layout=layout)


def make_header():
  x = [
    # Left - Headings
    make_red_heading_div(),
    # Right - Image
    html.Div(
      [
        html.Img(
          src='data:image/png;base64,{}'.format(logo.decode()),
          style={'height': '90px',
                 'align': 'right',
                 'margin-top': 20,
                 'margin-left': 20,
                 'margin-right': 0,
                 }
        ),
      ],
      className='six columns',
      style={'align': 'right',
             'margin-left': 0,
             'margin-right': 0,
             }
    ),
  ]
  return x


def make_red_heading_div():
  style = {'textAlign': 'left',
           'font-size': 36,
           'color': rc.RMIT_White,
           'font-family': 'Sans-serif',
           'font-weight': 'bold',
           'margin-left': 20,
           'margin-bottom': 5,
           'margin-top': 5,
           'backgroundColor': rc.RMIT_Red,
           'line-height': 'normal'}
  
  div = html.Div(
    [
      html.Div(children='SEMESTER 1, 2018 MICROSURGERY OUTCOMES', style=style),
    ],
    className='six columns',
    style={'backgroundColor': rc.RMIT_Red,
           'margin-left': 0,
           'margin-right': 0,
           }
  )
  return div


def make_blue_heading(improved, gts_75):
  style1 = {'text-align': 'center',
            'font-size': 40,
            'font-family': 'Sans-serif',
            'color': rc.RMIT_Lemon,
            'margin-left': 30,
            'margin-right': 0,
            'line-height': 'normal'}
  
  style2 = {'textAlign': 'justify',
            'font-size': 22,
            'font-family': 'Sans-serif',
            'font-weight': 'light',
            'color': rc.RMIT_White,
            'margin-left': 30,
            'margin-right': 0,
            'line-height': '90%'}
  
  style3 = {'text-align': 'center',
            'font-size': 40,
            'font-family': 'Sans-serif',
            'color': rc.RMIT_Lemon,
            'margin-left': 0,
            'margin-right': 0,
            'margin-top': 0,
            'line-height': 'normal'}
  
  style4 = {'text-align': 'center',
            'font-size': 50,
            'font-family': 'Sans-serif',
            'color': rc.RMIT_Lemon,
            'margin-left': 50,
            'margin-right': 0,
            'margin-top': 0,
            'line-height': 'normal'}
  
  style5 = {'textAlign': 'right',
            'font-size': 22,
            'font-family': 'Sans-serif',
            'font-weight': 'light',
            'color': rc.RMIT_White,
            'margin-left': 30,
            'margin-right': 0,
            'line-height': '90%'}
  
  x = [
    html.Div(
      [
        html.Div(
          [
            html.P(children='{}'.format(len(df_courses)), style=style4),
          ],
          className='three columns',
        ),
        html.Div(
          [
            html.P(children='Microsurgery courses', style=style2),
            html.P(children='with CES data', style=style2),
          ],
          className='nine columns',
        ),
      ],
      className='twelve columns',
      style={'margin-top': 10,
             'margin-bottom': 0,
             'backgroundColor': rc.RMIT_DarkBlue
             }
    ),
    html.Div(
      [
        html.Div(
          [
            html.P(children='Microsurgery courses', style=style5),
            html.P(children='achieved a GTS of 75+', style=style5),
          ],
          className='nine columns',
          style={'margin': 0}
        ),
        html.Div(
          [
            html.P(children='{}%'.format(gts_75), style=style3),
          ],
          className='three columns',
          style={'margin-right': 0}
        ),
      ],
      className='twelve columns',
      style={'margin-top': 0,
             'margin-bottom': 5,
             'margin-right': 0,
             'margin-left': 0,
             'backgroundColor': rc.RMIT_DarkBlue}
    ),
    html.Div(
      [
        html.Div(
          [
            html.P(children='{}%'.format(improved), style=style1),
          ],
          className='three columns',
        ),
        html.Div(
          [
            html.P(children='Microsurgery courses', style=style2),
            html.P(children='achieved > 3% GTS uplift', style=style2),
          ],
          className='nine columns',
        
        ),
      ],
      className='twelve columns',
      style={'margin-top': 10,
             'margin-bottom': 5,
             'backgroundColor': rc.RMIT_DarkBlue
             }
    ),
  ]
  return x


# Setup app
app = dash.Dash()
app.scripts.config.serve_locally = True
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# Create app layout
app.layout = html.Div(
  [
    # Heading
    html.Div(
      className='row',
      style={'margin-top': 0,
             'margin-left': 0,
             'margin-right': 0,
             'margin-bottom': 0,
             'backgroundColor': rc.RMIT_White,
             },
      children=make_header(),
    ),
    # First Row
    html.Div(
      className='row',
      style={'margin-bottom': 10,
             'margin-left': 0,
             'margin-right': 0,
             'backgroundColor': rc.RMIT_DarkBlue,
             },
      children=[
        # GTS Improvement
        html.Div(
          className='six columns',
          style={'margin-left': 0,
                 'margin-right': 0,
                 'margin-top': 0,
                 'backgroundColor': rc.RMIT_White,
                 },
          children=[
            html.P(children='Mean Course GTS Improvement',
                   style={'text-align': 'center',
                          'font-size': 16,
                          'font-family': 'Sans-serif',
                          'font-weight': 'Bold',
                          'color': rc.RMIT_Black,
                          'line-height': '140%',
                          'margin-left': 0,
                          'margin-right': 0,
                          'margin-top': 10,
                          'margin-bottom': 0,
                          'backgroundColor': rc.RMIT_White,
                          },
                   ),
            dcc.Graph(
              id='gts-graph1',
              figure=create_improve_bar(['2017', '2018'],
                                        get_avg_course_improve(cur, 'gts'),
                                        381,
                                        180,
                                        maxy=90)
            )
          ],
        ),
        # Blue stats
        html.Div(
          className='six columns',
          style={'backgroundColor': rc.RMIT_DarkBlue,
                 'margin-left': 0,
                 'margin-right': 0},
          children=make_blue_heading(
            int(round(100.0 * len(df_courses.loc[df_courses['gts_diff'] > 3]) / len(df_courses), 0)),
            int(round(100.0 * len(df_courses.loc[df_courses['gts_2018'] > 75]) / len(df_courses), 0))),
        ),
      ],
    ),
    # Second Row
    html.Div(
      className="row",
      style={'margin-left': 0,
             'margin-right': 0,
             'margin-top': 0},
      children=[
        # GTS Factors
        html.Div(
          className="six columns",
          style={'margin-left': 0,
                 'margin-right': 0,
                 'margin-top': 0},
          children=[
            html.P(children='Mean GTS Item Factor (HE) Improvement',
                   style={'text-align': 'center',
                          'font-size': 16,
                          'font-weight': 'Bold',
                          'font-family': 'Sans-serif',
                          'color': rc.RMIT_Black,
                          'line-height': '140%',
                          'margin-left': 0,
                          'margin-right': 0,
                          'margin-top': 0,
                          'margin-bottom': 0,
                          'backgroundColor': rc.RMIT_White, },
                   ),
            # Perceived Effort
            html.Div(
              className="six columns",
              style={'margin-left': 0,
                     'margin-right': 0,
                     'margin-top': 0},
              children=[
                html.Div(
                  [
                    dcc.Graph(id='pe-graph',
                              figure=create_improve_bar(
                                ['2017', '2018'],
                                get_avg_course_improve(cur, 'pe', table='microsurgery_2018_sem1_benchmarks_all_pe_se'),
                                200,
                                180,
                                maxy=90)
                              ),
                    html.P(children='Perceived Effort',
                           style={'text-align': 'center',
                                  'font-size': 14,
                                  'font-family': 'Sans-serif',
                                  'color': rc.RMIT_Black,
                                  'line-height': '140%',
                                  'margin-left': 0,
                                  'margin-right': 0,
                                  'margin-top': 0,
                                  'margin-bottom': 0,
                                  'backgroundColor': rc.RMIT_White, },
                           ),
                  ]
                )
              ]
            ),
            # Student Engagement
            html.Div(
              className="six columns",
              style={'margin-left': 0,
                     'margin-right': 0,
                     'margin-top': 0},
              children=[
                html.Div(
                  [
                    dcc.Graph(id='se-graph',
                              figure=create_improve_bar(
                                ['2017', '2018'],
                                get_avg_course_improve(cur, 'sei', table='microsurgery_2018_sem1_benchmarks_all_pe_se'),
                                200,
                                180,
                                maxy=90)
                              ),
                    html.P(children='Student Engagement',
                           style={'text-align': 'center',
                                  'font-size': 14,
                                  'font-family': 'Sans-serif',
                                  'color': rc.RMIT_Black,
                                  'line-height': '140%',
                                  'margin-left': 0,
                                  'margin-right': 0,
                                  'margin-top': 0,
                                  'margin-bottom': 0,
                                  'backgroundColor': rc.RMIT_White, },
                           ),
                  ]
                )
              ]
            ),
          ],
        ),
        html.Div(
          className='six columns',
          style={'margin-left': 0,
                 'margin-right': 0,
                 'margin-top': 0},
          children=[
            html.P(children='Mean Course OSI Improvement',
                   style={'text-align': 'center',
                          'font-size': 16,
                          'font-family': 'Sans-serif',
                          'font-weight': 'Bold',
                          'color': rc.RMIT_Black,
                          'line-height': '140%',
                          'margin-left': 0,
                          'margin-right': 0,
                          'margin-top': 0,
                          'margin-bottom': 0,
                          'backgroundColor': rc.RMIT_White, },
            
                   ),
            dcc.Graph(
              id='osi-graph1',
              figure=create_improve_bar(['2017', '2018'],
                                        get_avg_course_improve(cur, 'osi'),
                                        381,
                                        180,
                                        maxy=90)
            )
          ],
        )
      ],
    ),
    # Courses GTS change Graph Div
    html.Div(
      className='row',
      style={'margin': 0},
      children=[
        # Graph Title
        html.Div(
          className='row',
          children=['Percentage Change in Microsurgery Courses GTS'],
          style={'backgroundColor': rc.RMIT_Red,
                 'textAlign': 'center',
                 'font-size': 28,
                 'color': rc.RMIT_White,
                 'font-family': 'Sans-serif',
                 'font-weight': 'normal',
                 'line-height': '150%',
                 'align': 'center',
                 'margin-top': 0,
                 },
        ),
        # Courses GTS change Graph
        html.Div(
          className='row',
          style={'backgroundColor': rc.RMIT_DarkBlue,
                 'margin': 0},
          children=[
            dcc.Graph(
              id='gts-graph_courses',
              figure=create_course_improve_bar(
                x=df_courses['course_code'].tolist(),
                y=df_courses['gts_diff'].tolist(),
                width=780,
                height=400)
            ),
          ],
        ),
      ],
    ),
    # School Performance
    html.Div(
      className="row",
      style={'margin-left': 0,
             'margin-right': 0,
             'margin-top': 0,
             'backgroundColor': rc.RMIT_Red,
             },
      children=[
        # Header
        html.Div(
          className="four columns",
          style={'margin-left': 0,
                 'margin-right': 0,
                 'margin-top': 0},
          children=[
            html.P(
              children='Microsurgery Courses with GTS Above School Targets',
              style={'text-align': 'center',
                     'font-size': 20,
                     'font-family': 'Sans-serif',
                     'color': rc.RMIT_White,
                     'line-height': '140%',
                     'margin-left': 10,
                     'margin-right': 0,
                     'margin-top': 0,
                     'margin-bottom': 0,
                     },
            ),
          ],
        ),
        # School Stats
        html.Div(
          className="three columns",
          style={'margin-left': 20,
                 'margin-right': 0,
                 'margin-top': 10},
          children=[
            html.P(
              children='2017: {}%'.format(get_school_targets_improve(2017, decimal_places=0)),
              style={'text-align': 'left',
                     'font-size': 30,
                     'font-weight': 'Bold',
                     'font-family': 'Sans-serif',
                     'color': rc.RMIT_DarkBlue,
                     'line-height': '140%',
                     'margin-left': 0,
                     'margin-right': 0,
                     'margin-top': 0,
                     'margin-bottom': 0,
                     },
            ),
            html.P(
              children='2018: {}%'.format(get_school_targets_improve(2018, decimal_places=0)),
              style={'text-align': 'left',
                     'font-size': 30,
                     'font-weight': 'Bold',
                     'font-family': 'Sans-serif',
                     'color': rc.RMIT_Green,
                     'line-height': '140%',
                     'margin-left': 0,
                     'margin-right': 0,
                     'margin-top': 0,
                     'margin-bottom': 0,
                     },
            ),
          ],
        ),
        html.Div(
          className="five columns",
          style={'margin-left': 15,
                 'margin-right': 10,
                 'margin-top': 5,
                 'margin-bottom': 7,
                 'backgroundColor': rc.RMIT_White,
                 'border': 'solid'},
          children=[
            html.P(
              children='Graphs Legend',
              style={'text-align': 'center',
                     'font-size': 16,
                     'font-family': 'Sans-serif',
                     'color': rc.RMIT_Black,
                     'line-height': '140%',
                     'margin-left': 0,
                     'margin-right': 0,
                     'margin-top': 0,
                     'margin-bottom': 2,
                     'backgroundColor': rc.RMIT_White,
                     },
            ),
            html.P(
              children='2016 & 2017 (average)',
              style={'text-align': 'center',
                     'font-size': 16,
                     'font-weight': 'Bold',
                     'font-family': 'Sans-serif',
                     'color': rc.RMIT_White,
                     'line-height': '160%',
                     'margin-left': 10,
                     'margin-right': 10,
                     'margin-top': 0,
                     'margin-bottom': 5,
                     'backgroundColor': rc.RMIT_DarkBlue
                     },
            ),
            html.P(
              children='2018 Semester 1'.format(get_school_targets_improve(2018, decimal_places=0)),
              style={'text-align': 'center',
                     'font-size': 16,
                     'font-weight': 'Bold',
                     'font-family': 'Sans-serif',
                     'color': rc.RMIT_Black,
                     'line-height': '160%',
                     'margin-left': 10,
                     'margin-right': 10,
                     'margin-top': 0,
                     'margin-bottom': 5,
                     'backgroundColor': rc.RMIT_Green
                     },
            ),
          ]
        ),
      ],
    ),
  ],
  style={'width': '21cm',
         'height': '29.7cm',
         'top-margin': '50',
         'bottom-margin': '50',
         'right-margin': '25',
         'left-margin': '25',
         'border': 'solid',
         },
)

# In[]:
# More Helper functions

if __name__ == '__main__':
  app.run_server(debug=True)
  
  '''
    # Extra Graphs
    html.Div(
      [
        html.Div(
          [
            html.P(children='Average Microsurgery Courses GTS',
                   style={'text-align': 'center',
                          'font-size': 16,
                          'font-family': 'Sans-serif',
                          'font-weight': 'Bold',
                          'color': rc.RMIT_Black,
                          'line-height': '100%',
                          'margin': 0,
                          'border': 'dotted'},

                   ),
            dcc.Graph(
              id='gts-graph',
              figure=create_improve_bar(['2017', '2018'],
                                        [66.6, 76.6],
                                        295, 160,
                                        maxy=90),
              style={'border': 'dotted'},
            )
          ],
          className='five columns',
          style={'border': 'dotted'}
        ),
        html.Div(
          [],
          className='four columns',
        ),
        html.Div(
          [
            html.P(children='Average Microsurgery Courses OSI',
                   style={'text-align': 'middle',
                          'font-size': 16,
                          'font-family': 'Sans-serif',
                          'font-weight': 'Bold',
                          'color': rc.RMIT_Black,
                          'line-height': '100%',
                          'margin': 0,
                          'border': 'dotted'},

                   ),
            dcc.Graph(
              id='osi-graph',
              figure=create_improve_bar(['2017', '2018'],
                                        [62.0, 71.2],
                                        295, 160,
                                        maxy=90),
              style={'border': 'dotted'},
            )
          ],
          className='five columns',
          style={'border': 'dotted'}
        )
      ],
      className='twelve columns',
    ),
    '''
