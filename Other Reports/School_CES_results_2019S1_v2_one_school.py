import base64
import flask
import os
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from tabulate import tabulate

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc

from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
)

from School_performance_report import (
  create_school_RMIT_graph,
  create_CoB_graph
)


'''------------------------------------- Set Inputs  --------------------------------'''

year = 2019
semester = 2
start_year = 2015
end_year = 2019
school = 'VBE'

# Setup app
app = dash.Dash(__name__)
app.css.config.serve_locally = True
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
con, postgres_cur = connect_to_postgres_db(con_string)


'''------------------------Get Images---------------------'''
# header image
image_filename = 'C:\\Peter\\CoB\\logos\\L&T_Transparent_200.png'  # replace with your own image
logo = base64.b64encode(open(image_filename, 'rb').read())


'''------------------------Create Dataframes-----------------------'''
qry = ' SELECT \n' \
      '   year, semester, level, school_name_short, colour, colour_html, \n' \
      '   population, gts, osi, mgts, mosi\n' \
      ' FROM ces.vw146_school_bus_for_graph \n' \
      " WHERE  \n" \
      "   year >= {0} AND year <= {1} \n" \
      " UNION \n" \
      ' SELECT \n' \
      '   year, semester, level, college_name_short, colour, colour_html, \n' \
      '   population, gts, osi, mgts, mosi \n' \
      ' FROM ces.vw157_college_for_graph \n' \
      " WHERE  \n" \
      "   year >= {0} AND year <= {1} \n" \
      " ORDER BY year, semester, level, school_name_short \n" \
      "".format(start_year, end_year);


df_schools_data = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)


'''------------------------------ Create Dash functions -----------------------------------'''
def make_header():
  x = [
    # Left - Headings
    make_red_heading_div(),
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
    className='twelve columns',
    style={'backgroundColor': rc.RMIT_Red,
           'margin-left': 0,
           'margin-right': 0,
           }
  )
  return div


def make_ces_measure_section(measure, df=df_schools_data, start_year=2015, end_year=2018, school=None):
  if school == None:
    graph_title = 'Course Experience Survey - {} Percent Agree'.format(measure.upper())
  else:
    graph_title = 'Course Experience Survey - {} Percent Agree ({})'.format(measure.upper(),
                                                                            school)
    
  div = \
    html.Div(
      className='row',
      style={'margin-bottom': 0,
             'margin-left': 0,
             'margin-right': 0,
             'backgroundColor': rc.RMIT_White,
             },
      children=[
        # Graph Title #################################################
        html.Div(
          className='row',
          style={'margin-bottom': 0,
                 'margin-left': 4,
                 'margin-right': 4,
                 'backgroundColor': rc.RMIT_DarkBlue,
                 },
          children=[
            
            html.Div(
              className='row',
              children=[graph_title],
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
        # Table ################################################################
        html.Div(
          className='row',
          style={'margin-bottom': 0,
                 'margin-left': 0,
                 'margin-right': 0,
                 'margin-top': 0,
                 'backgroundColor': rc.RMIT_White,
                 },
          
          children=[
            html.Div(
              className='7 columns',
              style={
                'width': '62.5%',
                'margin-bottom': 0,
                     'margin-left': 0,
                     'margin-right': 0,
                     'margin-top': 0,
                     'backgroundColor': rc.RMIT_White,
                     },
    
              children=[
                dcc.Graph(
                  id='{}-table'.format(measure),
                  figure=generate_school_ces_pd_table(df, start_year, end_year, measure, school),
                  style={'margin': 0,
                         'margin-top': 0,
                         'margin-left': 25,
                         'margin-right': 0,
                         'backgroundColor': rc.RMIT_White},
                ),
              ],
            ),
            html.Div(
              className='5 columns',
              style={
                'width': '37.5%',
                'margin-bottom': 0,
                'margin-left': 0,
                'margin-right': 0,
                'margin-top': 0,
                'color': rc.RMIT_DarkBlue,
                'line-height': '110%',
                'backgroundColor': rc.RMIT_White,
                'text-align': 'left',
                'font-size': 16,
                'font-family': 'Sans-serif',
              },
    
              children=[
                html.P(
                  children=['The values presented are the {} Percent Agree.'
                            ''.format(measure.upper())],
                  style={
                    'margin-top': 50,
                    'margin-left': 15,
                    'margin-right': 5,
                  },
                ),
                html.P(
                  children=['This is the percentage of all student responses, for the school,'
                            ' that were an Agree or Strongly Agree'
                            ],
                  style={
                    'margin-left': 15,
                    'margin-right': 5,

                  },
                  
                ),
                html.P(
                  children=['This methodology treats all student responses equally.'
                            ],
                  style={
                    'margin-left': 15,
                    'margin-right': 5,
                  },
                ),
                html.P(
                  children=['Hence the larger course'
                            ' the more influence it has on the overall school result.'
                            ],
                  style={
                    'margin-left': 15,
                    'margin-right': 5,
                  },
                ),
              ],
            ),
          ],
        ),
        # Semester Titles #############################################
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
              style={'margin-left': 10,
                     'margin-right': 5,
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
        # Graphs #############################################################
        html.Div(
          className='row',
          style={'margin-bottom': 0,
                 'margin-left': 0,
                 'margin-right': 0,
                 'margin-top': 0,
                 'backgroundColor': rc.RMIT_White,
                 },
          
          children=[
            # OSI Sem 1 Graph
            html.Div(
              className='six columns',
              style={'margin-left': 0,
                     'margin-right': 10,
                     'margin-top': 0,
                     'backgroundColor': rc.RMIT_White,
                     },
              
              children=[
                dcc.Graph(
                  id='{}-graph1'.format(measure),
                  figure=create_school_RMIT_graph(
                    df1=df,
                    measure=measure,
                    start_year=start_year, end_year=end_year,
                    semester=1,
                    height=340,
                    width=530,
                    background='#FFFFFF',
                    school=school)
                )
              ],
            ),
            # OSI Sem 2 Graph
            html.Div(
              className='six columns',
              style={'margin-left': 20,
                     'margin-right': 0,
                     'margin-top': 0,
                     'backgroundColor': rc.RMIT_White,
                     },
              
              children=[
                dcc.Graph(
                  id='{}-graph2'.format(measure),
                  figure=create_school_RMIT_graph(
                    df1=df,
                    measure=measure,
                    start_year=start_year, end_year=end_year,
                    semester=2,
                    height=340,
                    width=530,
                    background='#FFFFFF',
                    school=school)
                )
              ],
            ),
          ],
        ),
      ],
    )
  return div


def generate_school_ces_pd_table(df1, start_year, end_year, measure, school=None):
  f_df = df1.loc[(df1['year'] >= start_year)
                 & (df1['year'] <= end_year)
                 & (df1['school_name_short'] != 'CPO')]
  f_df = f_df.round({'{}'.format(measure): 1})
  
  f_df_cobhe = f_df.loc[(f_df['school_name_short'] == 'CoB') & (f_df['level'] == 'HE')]
  f_df_coball = f_df.loc[(f_df['school_name_short'] == 'CoB') & (f_df['level'] == 'NA')]
  
  if school == None:
    width = 640
    f_df_acct = f_df.loc[(f_df['school_name_short'] == 'ACCT')]
    f_df_bitl = f_df.loc[(f_df['school_name_short'] == 'BITL')]
    f_df_efm = f_df.loc[(f_df['school_name_short'] == 'EFM')]
    f_df_gsbl = f_df.loc[(f_df['school_name_short'] == 'GSBL')]
    f_df_mgt = f_df.loc[(f_df['school_name_short'] == 'MGT')]
    f_df_vbehe = f_df.loc[(f_df['school_name_short'] == 'VBE') & (f_df['level'] == 'HE')]
    f_df_vbeve = f_df.loc[(f_df['school_name_short'] == 'VBE') & (f_df['level'] == 'VE')]
    f_df_cobhe = f_df.loc[(f_df['school_name_short'] == 'CoB') & (f_df['level'] == 'HE')]
    f_df_coball = f_df.loc[(f_df['school_name_short'] == 'CoB') & (f_df['level'] == 'NA')]
  
  
    h = [' <br>Year<br><br>', ' <br>S<br><br>',
         ' <br>ACCT<br>____<br>', ' <br>BITL<br>____<br>',
         ' <br>EFM<br>____<br>', ' <br>GSBL<br>____<br>',
         ' <br>MGT<br>____<br>',
         'VBE<br>(HE)<br>____<br>', 'VBE<br>(VE)<br>......<br>',
         'CoB<br>(HE)<br>____<br>', 'CoB<br>(All)<br><br>'
         ]
    trace = go.Table(
      type='table',
      columnorder=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
      columnwidth=[15, 10, 20, 20, 20, 20, 20, 20, 20, 20, 20],
      header=dict(line=dict(color=[rc.RMIT_White, rc.RMIT_White,
                                   rc.RMIT_White, rc.RMIT_White,
                                   rc.RMIT_White, rc.RMIT_White,
                                   rc.RMIT_White,
                                   rc.RMIT_White, rc.RMIT_White,
                                   rc.RMIT_Black, rc.RMIT_Black
                                   ]),
                  values=h,
                  align='center',
                  font=dict(size=18,
                            color=[rc.RMIT_White, rc.RMIT_White,
                                   f_df_acct.iloc[0]['colour_html'], f_df_bitl.iloc[0]['colour_html'],
                                   f_df_efm.iloc[0]['colour_html'], f_df_gsbl.iloc[0]['colour_html'],
                                   f_df_mgt.iloc[0]['colour_html'],
                                   f_df_vbehe.iloc[0]['colour_html'], f_df_vbeve.iloc[0]['colour_html'],
                                   f_df_cobhe.iloc[0]['colour_html'], f_df_coball.iloc[0]['colour_html']
                                   ]
                            ),
                  height=32,
                  fill=dict(color=[rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                                   rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                                   rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                                   rc.RMIT_DarkBlue,
                                   rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                                   rc.RMIT_White, rc.RMIT_White
                                   ])
                  ),
      cells=dict(line=dict(color=[rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_White,
                                  rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_White, rc.RMIT_White
                                  ]),
                 values=[f_df_acct.year, f_df_acct.semester,
                         f_df_acct['{}'.format(measure)], f_df_bitl['{}'.format(measure)],
                         f_df_efm['{}'.format(measure)], f_df_gsbl['{}'.format(measure)],
                         f_df_mgt['{}'.format(measure)],
                         f_df_vbehe['{}'.format(measure)], f_df_vbeve['{}'.format(measure)],
                         f_df_cobhe['{}'.format(measure)], f_df_coball['{}'.format(measure)]
                         ],
                 font=dict(size=12,
                           color=[rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_Black, rc.RMIT_Black,
                                  rc.RMIT_Black, rc.RMIT_Black,
                                  rc.RMIT_Black,
                                  rc.RMIT_Black, rc.RMIT_Black,
                                  rc.RMIT_White, rc.RMIT_White]),
                 height=25,
                 fill=dict(
                   color=[rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                          rc.RMIT_Arctic, rc.RMIT_Arctic,
                          rc.RMIT_Azure, rc.RMIT_Azure,
                          rc.RMIT_Arctic,
                          rc.RMIT_Azure, rc.RMIT_Azure,
                          f_df_cobhe.iloc[0]['colour_html'], f_df_coball.iloc[0]['colour_html'],
                          ]),
                 ),
    )
  elif school=='VBE':
    width = 650
    f_df_vbehe = f_df.loc[(f_df['school_name_short'] == 'VBE') & (f_df['level'] == 'HE')]
    f_df_vbeve = f_df.loc[(f_df['school_name_short'] == 'VBE') & (f_df['level'] == 'VE')]
    h = ['Year<br><br>', 'S<br><br>',
         'VBE (HE)<br>  _____<br>', 'VBE (VE)<br>  .......<br>',
         'CoB (HE)<br>  _____<br>',
         'VBE (HE)<br>   mean<br>', 'VBE (VE)<br>   mean<br>',
         'CoB (HE)<br>   mean<br>',
         ]
    trace = go.Table(
      type='table',
      columnorder=(1, 2, 3, 4, 5, 6, 7, 8),
      columnwidth=[10, 5, 20, 20, 20, 20, 20, 20],
      header=dict(line=dict(color=[rc.RMIT_White, rc.RMIT_White,
                                   rc.RMIT_White, rc.RMIT_White,
                                   rc.RMIT_Black,
                                   rc.RMIT_White, rc.RMIT_White,
                                   rc.RMIT_Black
                                   ]),
                  values=h,
                  align='center',
                  font=dict(size=18,
                            color=[rc.RMIT_White, rc.RMIT_White,
                                   f_df_vbehe.iloc[0]['colour_html'], f_df_vbeve.iloc[0]['colour_html'],
                                   f_df_cobhe.iloc[0]['colour_html'],
                                   f_df_vbehe.iloc[0]['colour_html'], f_df_vbeve.iloc[0]['colour_html'],
                                   f_df_cobhe.iloc[0]['colour_html']
                                   ]
                            ),
                  height=30,
                  fill=dict(color=[rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                                   rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                                   rc.RMIT_White,
                                   rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                                   rc.RMIT_White
                                   ])
                  ),
      cells=dict(line=dict(color=[rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_White,
                                  rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_White
                                  ]),
                 values=[f_df_vbehe.year, f_df_vbehe.semester,
                         f_df_vbehe['{}'.format(measure)], f_df_vbeve['{}'.format(measure)],
                         f_df_cobhe['{}'.format(measure)],
                         f_df_vbehe['m{}'.format(measure)], f_df_vbeve['m{}'.format(measure)],
                         f_df_cobhe['m{}'.format(measure)]
                         ],
                 font=dict(size=12,
                           color=[rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_Black, rc.RMIT_Black,
                                  rc.RMIT_White,
                                  rc.RMIT_Black, rc.RMIT_Black,
                                  rc.RMIT_White
                                  ]),
                 height=26,
                 fill=dict(
                   color=[rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                          rc.RMIT_Arctic, rc.RMIT_Arctic,
                          f_df_cobhe.iloc[0]['colour_html'],
                          rc.RMIT_Arctic, rc.RMIT_Arctic,
                          f_df_cobhe.iloc[0]['colour_html']
                          ]),
                 ),
    )
  else:
    width = 600
    f_df_school = f_df.loc[(f_df['school_name_short'] == school)]
    h = ['Year<br><br>', 'S<br><br>',
         '{}<br>___<br>'.format(school), ' {}<br>mean<br>'.format(school),
         'CoB (HE)<br> _____<br>', 'CoB (HE)<br>   mean<br>'
         ]
    trace = go.Table(
      type='table',
      columnorder=(1, 2, 3, 4, 5, 6),
      columnwidth=[15, 10, 15, 15, 20, 20],
      header=dict(line=dict(color=[rc.RMIT_White, rc.RMIT_White,
                                   rc.RMIT_White, rc.RMIT_White,
                                   rc.RMIT_Black, rc.RMIT_Black
                                   ]),
                  values=h,
                  align='center',
                  font=dict(size=18,
                            color=[rc.RMIT_White, rc.RMIT_White,
                                   f_df_school.iloc[0]['colour_html'], f_df_school.iloc[0]['colour_html'],
                                   f_df_cobhe.iloc[0]['colour_html'], f_df_cobhe.iloc[0]['colour_html']
                                   ]
                            ),
                  height=30,
                  fill=dict(color=[rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                                   rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                                   rc.RMIT_White, rc.RMIT_White
                                   ])
                  ),
      cells=dict(line=dict(color=[rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_White, rc.RMIT_White
                                  ]),
                 values=[f_df_school.year, f_df_school.semester,
                         f_df_school['{}'.format(measure)], f_df_school['m{}'.format(measure)],
                         f_df_cobhe['{}'.format(measure)], f_df_cobhe['m{}'.format(measure)]
                         ],
                 font=dict(size=12,
                           color=[rc.RMIT_White, rc.RMIT_White,
                                  rc.RMIT_Black, rc.RMIT_Black,
                                  rc.RMIT_White, rc.RMIT_White]),
                 height=26,
                 fill=dict(
                   color=[rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                          rc.RMIT_Arctic, rc.RMIT_Arctic,
                          f_df_cobhe.iloc[0]['colour_html'], f_df_cobhe.iloc[0]['colour_html'],
                          ]),
                 ),
    )
  
  layout = go.Layout(width=width,
                     height=355,
                     margin=dict(b=10, l=10, r=10, t=10))
  data = [trace]
  fig = dict(data=data, layout=layout)
  return fig


# Create app layout
app.layout = html.Div(
  [
    html.Link(
      rel='stylesheet',
      href='/static/bWLwgP.css'
    ),
    html.Link(
      rel='stylesheet',
      href='/static/remove_undo.css'
    ),
    # Measures
    make_ces_measure_section('osi', df_schools_data, start_year, end_year, school),
    make_ces_measure_section('gts', df_schools_data,  start_year, end_year, school),
  ],
  style={'width': '29.4cm',
         'height': '20.25',
         'top-margin': '50',
         'bottom-margin': '50',
         'right-margin': '25',
         'left-margin': '25',
         'border': 'None',
         },
)

# Upload css formats
css_directory = 'C:\\Peter\\GitHub\\CoB\\Other Reports\\'
#stylesheets = ['bWLwgP.css', 'remove_undo.css']
#static_css_route = '/static/'
#print(css_directory)

@app.server.route('/static/<path:path>')
def static_file(path):
  static_folder = os.path.join(css_directory, 'static')
  return send_from_directory(static_folder, path)


if __name__ == '__main__':
  app.run_server(port=8050, host='127.0.0.3', debug=False)


'''
create_CoB_graph(
  df_schools_data,
  measure='gts',
  start_year=2015, end_year=2019,
  semester=1,
  height=600,
  width=1100,
  background='#FFFFFF')

create_CoB_graph(
  df_schools_data,
  measure='osi',
  start_year=2015, end_year=2019,
  semester=1,
  height=600,
  width=1100,
  background='#FFFFFF')

'''