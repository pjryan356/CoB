

import plotly.graph_objs as go

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc

from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
)
from tabulate import tabulate

import dash
import dash_core_components as dcc
import dash_html_components as html

import base64

from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
)

from Course_Enhancement_comparison import (
  create_ce_comparison_chart
)
year = 2019
semester = 1

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


'''------------------------Get Images---------------------'''
# header image
image_filename = 'C:\\Peter\\CoB\\logos\\L&T_Transparent_200.png'  # replace with your own image
logo = base64.b64encode(open(image_filename, 'rb').read())

def get_ce_courses(year, semester, table='vw204_ce_evaluation', ce=True):
  qry = ' SELECT level, course_code_ces, \n' \
        '   gts_pre, \n' \
        '   gts_post, \n' \
        '   gts_delta, \n' \
       '    osi_pre, \n' \
        '   osi_post, \n' \
        '   osi_delta \n' \
        ' FROM course_enhancement.{} \n' \
        ' WHERE ce = {} \n' \
        '     AND year = {} \n' \
        '     AND semester = {} \n' \
        '     AND gts_delta IS NOT NULL \n' \
        '     AND osi_delta IS NOT NULL \n' \
        ' ORDER BY gts_delta \n'.format(table, ce, year, semester)
  df = db_extract_query_to_dataframe(qry, cur)
  return df

df_courses = get_ce_courses(year, semester)

df_courses = get_ce_courses(year, semester, table='vw214_ce_evaluation_reliable')

df_courses_nce = get_ce_courses(year, semester, table='vw214_ce_evaluation_reliable', ce=False)



print(tabulate(df_courses.sort_values(by=['course_code_ces']), headers='keys'))

def create_course_improve_bar(x, y, width, height):
  bar_colours = []

  for val in y:
    if val != None:
      if val <= 0:
        bar_colours.append(rc.RMIT_Red)
      else:
        bar_colours.append(rc.RMIT_Green)
    else:
      bar_colours.append(rc.RMIT_Black)
  
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
      range=[-50, 50],
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
    margin=dict(b=10, l=10, r=0, t=10),
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
          style={'height': '120px',
                 'align': 'center',
                 'margin-top': 15,
                 'margin-left': 80,
                 'margin-right': 80,
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

  style = {'text-align': 'center',
           'font-size': 36,
           'color': rc.RMIT_White,
           'font-family': 'Sans-serif',
           'font-weight': 'bold',
           'margin-left': 10,
           'margin-right': 10,
           'margin-bottom': 10,
           'margin-top': 10,
           'backgroundColor': rc.RMIT_Red,
           'line-height': 'normal'}
  
  div = html.Div(
    children=[
      html.P(children='Course Enhancement Semester {0}   {1}'.format(semester, year),
             style=style),
    ],
    className='six columns',
    style={'backgroundColor': rc.RMIT_Red,
           'margin-left': 0,
           'margin-right': 0,
           }
  )
  return div


def make_blue_heading(df1):
  style1 = {'text-align': 'center',
            'font-size': 40,
            'font-family': 'Sans-serif',
            'color': rc.RMIT_Lemon,
            'margin-left': 10,
            'margin-right': 10,
            'margin-bottom': 10,
            'margin-top': 10,
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
            'margin-left': 25,
            'margin-right': 0,
            'margin-top': 0,
            'line-height': 'normal'}
  
  style4 = {'text-align': 'center',
            'font-size': 45,
            'font-family': 'Sans-serif',
            'color': rc.RMIT_Lemon,
            'margin-left': 25,
            'margin-right': 0,
            'margin-bottom': 0,
            'line-height': 'normal'}
  
  style5 = {'textAlign': 'left',
            'font-size': 22,
            'font-family': 'Sans-serif',
            'font-weight': 'light',
            'color': rc.RMIT_White,
            'margin-left': 30,
            'margin-right': 0,
            'margin-top': 10,
            'margin-bottom': 0,
            'line-height': '90%'}
  
  x = [
    html.Div(
      [
        html.Div(
          [
            html.P(children='{}'.format(len(df1)), style=style4),
          ],
          className='three columns',
        ),
        html.Div(
          [
            html.P(children='Enhanced Courses', style=style2),
            html.P(children='with Reliable CES data', style=style2),
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
            html.P(children='Enhanced Courses that', style=style5),
            html.P(children='achieved a GTS of 75+', style=style5),
          ],
          className='nine columns',
          style={'margin': 0}
        ),
        html.Div(
          [
            html.P(
              children='{}%'.format(int(round(
                100.0 * len(df1.query('gts_post > 75')) / len(df1),
                0))
              ),
              style=style1),
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
            html.P(
              children='{}%'.format(int(round(
                100.0 * len(df1.query('gts_delta > 3')) / len(df1),
                0))
              ),
              style=style3),
          ],
          className='three columns',
        ),
        html.Div(
          [
            html.P(children='Enhanced Courses that ', style=style2),
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
      style={'margin-top': 4,
             'margin-left': 4,
             'margin-right': 4,
             'margin-bottom': 0,
             'backgroundColor': rc.RMIT_White,
             },
      children=make_header(),
    ),
    # First Row
    html.Div(
      className='row',
      style={'margin-bottom': 10,
             'margin-left': 4,
             'margin-right': 4,
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
            html.P(children='GTS Improvement (Course Mean)',
                   style={'text-align': 'center',
                          'font-size': 16,
                          'font-family': 'Sans-serif',
                          'font-weight': 'Bold',
                          'color': rc.RMIT_Black,
                          'line-height': '100%',
                          'margin-left': 0,
                          'margin-right': 0,
                          'margin-top': 10,
                          'margin-bottom': 0,
                          'backgroundColor': rc.RMIT_White,
                          },
                   ),
            dcc.Graph(
              id='gts-graph1',
              figure=create_improve_bar(['Pre', 'Post'],
                                        [round(df_courses['gts_pre'].mean(), 1),
                                         round(df_courses['gts_post'].mean(), 1)],
                                        377,
                                        180,
                                        maxy=90)
            )
          ],
        ),
        # Blue stats
        html.Div(
          className='six columns',
          style={'backgroundColor': rc.RMIT_DarkBlue,
                 'margin-left': 1,
                 'margin-right': 2},
          children=make_blue_heading(df_courses),
        ),
      ],
    ),
    # Second Row
    html.Div(
      className="row",
      style={'margin-left': 4,
             'margin-right': 4,
             'margin-top': 0},
      children=[
        # Past performance
        html.Div(
          className="six columns",
          style={'margin-left': 0,
                 'margin-right': 0,
                 'margin-top': 0,
                 'margin-bottom': 0},
          children=[
            html.P(children='Effectiveness (Mean Change in GTS)',
                   style={'text-align': 'center',
                          'font-size': 16,
                          'font-family': 'Sans-serif',
                          'font-weight': 'Bold',
                          'color': rc.RMIT_Black,
                          'line-height': '100%',
                          'margin-left': 0,
                          'margin-right': 0,
                          'margin-top': 0,
                          'margin-bottom': 0,
                          'backgroundColor': rc.RMIT_White,
                          },
                   ),
            dcc.Graph(
              id='past-ce',
              figure=create_ce_comparison_chart(
                cur,
                381,
                180,
                show_title=False,
                show_annotations=False,
                show_ylabel=False,
                show_pval=False,
                table='vw214_ce_evaluation_reliable'),
              style={'margin-left': 0,
                     'margin-right': 0,
                     'margin-top': 0,
                     'margin-bottom': 0,
                    }
            ),
          ],
        ),
        html.Div(
          className='six columns',
          style={'margin-left': 1,
                 'margin-right': 0,
                 'margin-top': 0},
          children=[
            html.P(children='OSI Improvement (Course Mean)',
                   style={'text-align': 'center',
                          'font-size': 16,
                          'font-family': 'Sans-serif',
                          'font-weight': 'Bold',
                          'color': rc.RMIT_Black,
                          'line-height': '100%',
                          'margin-left': 0,
                          'margin-right': 0,
                          'margin-top': 0,
                          'margin-bottom': 0,
                          'backgroundColor': rc.RMIT_White, },
            
                   ),
            dcc.Graph(
              id='osi-graph1',
              figure=create_improve_bar(['Pre', 'Post'],
                                        [round(df_courses['osi_pre'].mean(), 1),
                                         round(df_courses['osi_post'].mean(), 1)],
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
      style={'margin-left': 4,
             'margin-right': 4,
             'margin-top': 0},
      children=[
        # Graph Title
        html.Div(
          className='row',
          children=['Enhanced Courses (Change in GTS)'],
          style={'backgroundColor': rc.RMIT_Red,
                 'textAlign': 'center',
                 'font-size': 28,
                 'color': rc.RMIT_White,
                 'font-family': 'Sans-serif',
                 'font-weight': 'normal',
                 'line-height': '150%',
                 'align': 'center',
                 'margin-top': 2,
                 },
        ),
        # Courses GTS change Graph
        html.Div(
          className="six columns",
          style={'margin-left': 0,
                 'margin-right': 10,
                 'margin-top': 0,
                 'margin-bottom': 0},
          children=[
            html.Div(
              className='row',
              style={'backgroundColor': rc.RMIT_DarkBlue,
                     'margin': 0},
              children=[
                dcc.Graph(
                  id='gts-graph_courses_ce',
                  figure=create_course_improve_bar(
                    x=df_courses['course_code_ces'].tolist(),
                    y=df_courses['gts_delta'].tolist(),
                    width=389,
                    height=400)
                ),
              ],
            ),
          ],
        ),
        html.Div(
          className="six columns",
          style={'margin-left': 10,
                 'margin-right': 0,
                 'margin-top': 0,
                 'margin-bottom': 0},
          children=[
            html.Div(
              className='row',
              style={'backgroundColor': rc.RMIT_DarkBlue,
                     'margin': 0},
              children=[
                dcc.Graph(
                  id='gts-graph_courses_nce',
                  figure=create_course_improve_bar(
                    x=df_courses_nce['course_code_ces'].tolist(),
                    y=df_courses_nce['gts_delta'].tolist(),
                    width=389,
                    height=400)
                ),
              ],
            ),
          ],
        ),
      ],
    ),
    # School Performance
    html.Div(
      className="row",
      style={'margin-left': 4,
             'margin-right': 4,
             'margin-top': 10,
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
              children='Enhanced Courses with GTS above School Targets',
              style={'text-align': 'center',
                     'font-size': 20,
                     'font-family': 'Sans-serif',
                     'color': rc.RMIT_White,
                     'line-height': '140%',
                     'margin-left': 10,
                     'margin-right': 0,
                     'margin-top': 10,
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
              children='{}: {}%'.format(
                year-1,
                0
              ),
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
              children='{}: {}%'.format(
                year,
                0
              ),
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
                     'margin-left': 1,
                     'margin-right': 1,
                     'margin-top': 0,
                     'margin-bottom': 2,
                     'backgroundColor': rc.RMIT_White,
                     },
            ),
            html.P(
              children='Two Previous Offerings (average)',
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
              children='{} Semester {}'.format(year, semester),
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
            html.P(children='Mean Course Enhancement Courses GTS',
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
            html.P(children='Mean Course Enhancement Courses OSI',
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
