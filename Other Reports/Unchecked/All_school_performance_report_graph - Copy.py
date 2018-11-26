
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

from tabulate import tabulate

import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from IPython.display import display, HTML
from xhtml2pdf import pisa
import base64

import pandas as pd
import plotly.offline


#auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

import general.RMIT_colours as rc

from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
)

school = input("School short: ")

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


'''-------------------------------------------- Get Data -------------------------------------'''
 
def qry_school_history(school_name_short,
                       start_year=2014,
                       semester=None,
                       level='HE',
                       schema='ces',
                       table='vw998_school_from_course_summaries'):
  qry = ' SELECT t1.* \n' \
        ' FROM ({0}) t1 \n' \
        " WHERE school_name_short = '{1}' \n" \
        '   AND year >= {2} \n' \
        "   AND level = '{3}' \n" \
        ''.format(qry_school_history_details(schema, table),
                  school_name_short, start_year, level)
  if semester != None:
    qry += ' AND semester = {} \n'.format(semester)
  
  qry += 'ORDER BY year, semester, level \n'
  return qry
  
def qry_school_history_details(schema, table):
  qry = ' SELECT \n' \
        '   sch.*, \n' \
        '   sd.school_name_short, \n' \
        '   sd.colour_html, \n' \
        '   sd.colour_alt_html, \n' \
        '   st.gts_target, \n' \
        '   st.osi_target \n' \
        ' FROM ( \n' \
        '   SELECT \n' \
        '     year, semester, level, \n' \
        '     school_code, school_name, \n' \
        '     population, osi, gts \n' \
        '   FROM {0}.{1} \n' \
        '   ) sch \n' \
        ' LEFT JOIN ( \n' \
        '   SELECT \n' \
        '     school_code, \n' \
        '     school_name_short, \n' \
        '     colour_html,' \
        '     colour_alt_html \n' \
        '   FROM lookups.vw_bus_schools_colours) sd ON sch.school_code = sd.school_code::text \n' \
        ' LEFT JOIN ( \n' \
        '   SELECT \n' \
        '     year::integer AS year, \n' \
        '     school_code, \n' \
        '     gts_target, \n' \
        '     osi_target \n' \
        '   FROM ces.tbl_school_targets) st ON st.school_code = sch.school_code::text AND sch.year::int = st.year::int \n' \
        ' ORDER BY year, semester, level \n' \
        ''.format(schema, table)
  return qry


def line_trace_school_measure(school_name_short, measure='gts',
                              start_year=2014, end_year=2018,
                              level='HE',
                              semester=None,
                              dash_type=None,
                              colour_alt=False):
  qry = qry_school_history(
    school_name_short=school_name_short,
    level=level,
    start_year=start_year,
    semester=semester,
    schema='ces',
    table='vw998_school_from_course_summaries'
  )
  
  df1 = db_extract_query_to_dataframe(qry, cur, print_messages=False)
  if semester == 1:   df1 = df1.loc[df1['semester'] == 1]
  elif semester == 2: df1 = df1.loc[df1['semester'] == 2]
  
  x = [i - 0.5 for i in range(1, int(end_year)-int(start_year) + 2)]

  if colour_alt==True:
    colour = df1.iloc[0]['colour_alt_html']
  else:
    colour = df1.iloc[0]['colour_html']
  
  print(school_name_short, colour)
  # Create Semester 1 trace (solid)
  trace = go.Scatter(
    x=x,
    y=df1[measure].tolist(),
    name='<span style="color: {2}">{0} ({1})   </span>'.format(school_name_short, level, colour),
    text=None,
    textfont={'size': 14,
              'color': colour},
    line=go.Line(width=3,
                 color=colour,
                 dash=dash_type),
    marker=go.Marker(
      color=colour,
      size=8,
      symbol='diamond'
    ),
    connectgaps=False,
    mode='lines+markers',
    showlegend=True,
    textposition='bottom right'
  )
  return trace

def create_school_RMIT_graph(measure='gts',
                             start_year=2014, end_year=2018,
                             semester=1,
                             folder='C:\\Peter\\CoB\\CES\\2018_Semester_2\\',
                             height=600,
                             width=1100,
                             colour_alt=False,
                             background='#000000'):
  
  if background == '#000000':
    line_col = '#FFFFFF'
  else:
    line_col = None
  
  traces = []
  x = [i+0.5 for i in range(0, (int(end_year) - int(start_year) + 1))]
  xlabels = ['{}'.format(i) for i in range(int(start_year), int(end_year) + 1)]
  graph_title = 'Semester {1} School {0} (% Agree) by year'.format(measure.upper(), semester)
  for school in [['ACCT', 'HE'],
                 ['BITL', 'HE'],
                 ['EFM', 'HE'],
                 ['GSBL', 'HE'],
                 ['MGT', 'HE'],
                 ['VBE', 'HE'],
                 ['VBE', 'VE']]:
    
    if school[1] == 'VE': dash_type = 'dot'
    else: dash_type = None
    
    traces.append(line_trace_school_measure(
      school[0],
      measure='gts',
      start_year=start_year, end_year=end_year,
      level=school[1],
      semester=semester,
      dash_type=dash_type,
      colour_alt=colour_alt))
  
  fig = go.Figure(
    data=traces,
    layout=go.Layout(
      title=graph_title,
      titlefont={'size': 16,},
      showlegend=True,
      legend=dict(
        font=dict(size=12),
        orientation="h",
        bgcolor=background
      ),
      paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor=background,
      xaxis=dict(
        range=[0, int(end_year) - int(start_year) + 1],
        tickvals=x,
        tickfont={'size': 12},
        showgrid=False,
        ticktext=xlabels,
        ticks='outside',
        tick0=1,
        dtick=1,
        ticklen=5,
        zeroline=True,
        zerolinewidth=2,
           ),
      yaxis=dict(
        title='Percent Agree',
        titlefont={'size': 14},
        range=[64, 86],
        ticklen=5,
        tickfont={'size': 12},
        zeroline=True,
        zerolinewidth=2,
        gridcolor=line_col,
        layer="below traces",
      ),
      width=width,
      height=height,
      hovermode='closest',
      margin=dict(b=40, l=60, r=5, t=40),
      hidesources=True,
    )
  )
  filename = folder + 'school_comp_graph_{}_{}'.format(measure, end_year)
  plotly.offline.plot(fig, filename+'.html')
  #py.image.save_as(fig, filename+'.png')
  return fig

fig = create_school_RMIT_graph(
  measure='gts',
  start_year=2014, end_year=2018,
  semester=2,
  folder='C:\\Peter\\CoB\\CES\\2018_Semester_2\\',
  height=400,
  width=800,
  colour_alt=True,
  background='#FFFFFF')


def generate_ces_schools_table(semester=1, level='All'):
  h = ['<br><b>School</b><br>', '<br>Pop.<br>',
       '<br>2014<br>', '<br>2015<br>', '<br>2016<br>', '<br>2017<br>', '<br>2018<br>',
       '<br>Change<br>', '<br>Target<br>']

  qry = " SELECT \n " \
        "   * FROM ces.vw999_school_from_course_summaries_2018 \n" \
        " WHERE semester = {0}\n" \
        " UNION \n" \
        ' SELECT \n' \
        '   2 AS order1, \n' \
        '   * FROM ces.vw_college_summaries_table_percent \n' \
        " WHERE semester = {0} AND level = '{1}'\n" \
        " ORDER BY order1, name_short \n" \
        "".format(semester, level)

  df1 = db_extract_query_to_dataframe(qry, cur, print_messages=False)
  
  column_widths = [250, 60, 60, 60, 60, 60, 60, 60, 60]
  trace = go.Table(
    type='table',
    columnorder=(1, 2, 3, 4, 5, 6, 7, 8, 9),
    columnwidth=column_widths,
    header=dict(line=dict(color=rc.RMIT_White),
                values=h,
                font=dict(size=15,
                          color=rc.RMIT_White),
                height=40,
                format=dict(border='solid'),
                fill=dict(color=rc.RMIT_DarkBlue)
                ),
    cells=dict(line=dict(color=[rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_White]),
               values=[df1.name, df1.survey_population,
                       df1.gts_2014, df1.gts_2015, df1.gts_2016, df1.gts_2017, df1.gts_2018,
                       df1.gts_2018-df1.gts_2017, df1.gts_target],
               font=dict(size=12,
                         color=[rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_Black, rc.RMIT_Black,
                                rc.RMIT_Black, rc.RMIT_Black,
                                rc.RMIT_Black, rc.RMIT_White,
                                rc.RMIT_White]),
               height=30,
               format=dict(border='solid'),
               fill=dict(
                 color=[rc.RMIT_DarkBlue, rc.RMIT_Azure,
                        rc.RMIT_Arctic, rc.RMIT_Arctic,
                        rc.RMIT_Arctic, rc.RMIT_Arctic, rc.RMIT_Arctic,
                        rc.RMIT_Azure, rc.RMIT_Azure]),
               align=['left', 'right']
               ),
  )
  
  layout = go.Layout(title='<b>College of Business GTS</b> (Semester 1)',
                     width=sum(column_widths),
                     height=380,
                     margin=dict(b=10, l=10, r=10, t=40))
  data = [trace]
  
  fig = dict(data=data, layout=layout)
  plotly.offline.plot(fig, 'text' + '.html')
  return fig


#fig2 = generate_ces_schools_table(semester=2, level='All')
'''
 traces.append(trace_sem1)
  
  #Create Semester 2 trace (dashed)
  trace_sem2 = go.Scatter(
    x=x,
    y=df_2[measure].tolist(),
    name='Semester 2  ',
    text=None,
    line=go.Line(width=2,
                 color=df_2.iloc[0]['colour_html'],
                 dash='dot',),
    marker=go.Marker(
      color=df_2.iloc[0]['colour_html'],
      size=8,
      symbol='diamond'
    ),
    connectgaps=False,
    mode='lines+markers',
    showlegend=True,
    textposition='top center'
  )
  traces.append(trace_sem2)


  trace_target = go.Scatter(
    x=x,
    y=df_1['gts_target'].tolist(),
    name='Target',
    text=df_1['gts_target'].tolist(),
    textfont={'size': 14,
              'color': rc.RMIT_Black},
    line=go.Line(width=2, color=rc.RMIT_Black),
    marker=go.Marker(
      color=rc.RMIT_Black,
      size=8,
      symbol='square'
    ),
    connectgaps=False,
    mode='lines+markers+text',
    showlegend=True,
    textposition='bottom right')
  
  traces.append(trace_target)
  
  return None
  '''
