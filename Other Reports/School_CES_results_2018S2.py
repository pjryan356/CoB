

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

from School_performance_report import (
  get_school_data,
  create_school_RMIT_graph
)
year = 2018
semester = 2

start_year = 2015
end_year = 2019

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
con, postgres_cur = connect_to_postgres_db(con_string)


'''------------------------Get Images---------------------'''
# header image
image_filename = 'C:\\Peter\\CoB\\logos\\L&T_Transparent_200.png'  # replace with your own image
logo = base64.b64encode(open(image_filename, 'rb').read())


'''------------------------Get Data-----------------------'''
df_schools_data = get_school_data(start_year, postgres_cur)
#print(tabulate(df_schools_data, headers='keys'))


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
                 'align': 'center',
                 'margin-top': 5,
                 'margin-left': 100,
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
      html.P(children='CoB Schools    CES Results {1}'.format(semester, year),
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
  
  style5 = {'textAlign': 'left',
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
            html.P(children='{}'.format(len(df1)), style=style4),
          ],
          className='three columns',
        ),
        html.Div(
          [
            html.P(children='Course Enhancement', style=style2),
            html.P(children='courses with CES data', style=style2),
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
            html.P(children='Course Enhancement ', style=style5),
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
              style=style1),
          ],
          className='three columns',
        ),
        html.Div(
          [
            html.P(children='Course Enhancement ', style=style2),
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
    # 2nd Row
    # OSI Title
    html.Div(
      className='row',
      style={'margin-bottom': 0,
             'margin-left': 4,
             'margin-right': 4,
             'backgroundColor': rc.RMIT_DarkBlue,
             },
      children=[
        # Graph Title
        html.Div(
          className='row',
          children=['OSI'],
          style={'backgroundColor': rc.RMIT_DarkBlue,
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
      ],
    ),
    # 3rd Row
    # OSI Graphs Titles
    html.Div(
      className='row',
      style={'margin-bottom': 0,
             'margin-left': 4,
             'margin-right': 4,
             'backgroundColor': rc.RMIT_White,
             },
      children=[
        # Semester 1
        html.Div(
          className='six columns',
          style={'margin-left': 10,
                 'margin-right': 5,
                 'margin-top': 0,
                 'backgroundColor': rc.RMIT_White,
                 },
          children=[
            html.P(children='Semester 1',
                   style={'text-align': 'center',
                          'font-size': 16,
                          'font-family': 'Sans-serif',
                          'font-weight': 'Bold',
                          'color': rc.RMIT_White,
                          'line-height': '100%',
                          'margin-left': 5,
                          'margin-right': 5,
                          'margin-top': 2,
                          'margin-bottom': 2,
                          'backgroundColor': rc.RMIT_Blue,
                          },
                   ),
            ],
        ),
        # Semester 2
        html.Div(
          className='six columns',
          style={'margin-left': 5,
                 'margin-right': 10,
                 'margin-top': 0,
                 'backgroundColor': rc.RMIT_White,
                 },
          children=[
            html.P(children='Semester 2',
                   style={'text-align': 'center',
                          'font-size': 16,
                          'font-family': 'Sans-serif',
                          'font-weight': 'Bold',
                          'color': rc.RMIT_White,
                          'line-height': '100%',
                          'margin-left': 5,
                          'margin-right': 5,
                          'margin-top': 2,
                          'margin-bottom': 2,
                          'backgroundColor': rc.RMIT_Blue,
                          },
                   ),
          ],
        ),
      ],
    ),
    # 4th Row
    # OSI Graphs
    html.Div(
      className='row',
      style={'margin-bottom': 0,
             'margin-left': 0,
             'margin-right': 0,
             'margin-top': 0,
             'backgroundColor': rc.RMIT_White,
             },
      
      children=[
        #OSI Sem 1 Graph
        html.Div(
          className='six columns',
          style={'margin-left': 0,
                 'margin-right': 10,
                 'margin-top': 0,
                 'backgroundColor': rc.RMIT_White,
                 },

          children=[
            dcc.Graph(
              id='osi-graph1',
              figure=create_school_RMIT_graph(
                  df1=df_schools_data,
                  measure='osi',
                  start_year=2015, end_year=2018,
                  semester=1,
                  folder='H:\\Projects\\CoB\\CES\\School Reporting\\2018 S2\\',
                  height=400,
                  width=396,
                  background='#FFFFFF')
            )
          ],
        ),
        # OSI Sem 2 Graph
        html.Div(
          className='six columns',
          style={'margin-left': 0,
                 'margin-right': 0,
                 'margin-top': 0,
                 'backgroundColor': rc.RMIT_White,
                 },
    
          children=[
            dcc.Graph(
              id='osi-graph2',
              figure=create_school_RMIT_graph(
                df1=df_schools_data,
                measure='osi',
                start_year=2015, end_year=2018,
                semester=2,
                folder='H:\\Projects\\CoB\\CES\\School Reporting\\2018 S2\\',
                height=400,
                width=396,
                background='#FFFFFF')
            )
          ],
        ),
      ],
    ),

    # 5th Row
    # GTS Graph Div
    html.Div(
      className='row',
      style={'margin-left': 4,
             'margin-right': 4,
             'margin-top': 0},
      children=[
        # Graph Title
        html.Div(
          className='row',
          children=['GTS'],
          style={'backgroundColor': rc.RMIT_Blue,
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
        # Schools GTS Graphs Semester 1
        html.Div(
          className='row',
          style={'backgroundColor': rc.RMIT_DarkBlue,
                 'margin': 0},
          children=[
            dcc.Graph(
              id='gts-graph1',
              figure=create_school_RMIT_graph(
                  df1=df_schools_data,
                  measure='gts',
                  start_year=2015, end_year=2018,
                  semester=1,
                  folder='H:\\Projects\\CoB\\CES\\School Reporting\\2018 S2\\',
                  height=400,
                  width=790,
                  background='#FFFFFF',
                  graph_title='Semester 1')
            ),
          ],
        ),
        # Schools GTS Graphs Semester 2
        html.Div(
          className='row',
          style={'backgroundColor': rc.RMIT_DarkBlue,
                 'margin': 0},
          children=[
            dcc.Graph(
              id='gts-graph2',
              figure=create_school_RMIT_graph(
                df1=df_schools_data,
                measure='gts',
                start_year=2015, end_year=2018,
                semester=2,
                folder='H:\\Projects\\CoB\\CES\\School Reporting\\2018 S2\\',
                height=400,
                width=790,
                background='#FFFFFF',
                graph_title='Semester 2')
            ),
          ],
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
