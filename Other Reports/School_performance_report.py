import base64

import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.offline

from tabulate import tabulate

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc


from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
)



'''--------------------------------- Initialise Parameters  ----------------------------'''

folder = 'H:\\Projects\\CoB\\CES\\School Reporting\\2018 S2\\'

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
postgres_con, postgres_cur = connect_to_postgres_db(con_string)


'''-------------------------------------------- Get Data -------------------------------------'''
qry = ' SELECT * \n' \
      ' FROM ces.vw146_school_bus_for_graph \n' \
      "   WHERE year >= {}" \
      " ORDER BY school_code, level, year, semester" \
      "; \n".format(start_year)
 
df_schools_data = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)


def line_graph_school_measure(df1, school, level='HE', measure='gts',
                              start_year=2015, end_year=2019,
                              height=400,
                              width=800):
  
  df_school = df1.loc[df1['school_name_short'] == school]
  df_targets = df_school[['year', 'gts_target']].drop_duplicates()
  df_school = df_school.loc[df_school['level'] == level]
  
  df_1 = df_school.loc[df_school['semester'] == 1]
  df_2 = df_school.loc[df_school['semester'] == 2]
  

  #print(tabulate(df_school, headers='keys'))
  #print(tabulate(df_targets, headers='keys'))
  #print(end_year)
  
  # all traces for plotly
  traces = []
  xlabels = []
  
  for year in range(int(start_year), int(end_year) + 1):
    xlabels.append('{}<br>'.format(year))
  
  no_terms = len(xlabels)
  
  x = [i - 0.5 for i in range(1, no_terms + 1)]
  
  label_check = 0

  graph_title = '<b>CES ({2}):</b> {1} School {0}'.format(measure.upper(), df_school.iloc[0]['school_name'], level)
  
  data_label = []
  y = []
  label_check += 1
  
  # Create Semester 1 text
  sem1_text = [None for j in range(len(x)-1)]
  sem1_text.append(df_1.iloc[-1][measure])
  print(sem1_text)
  
  # Create Semester 1 trace (solid)
  trace_sem1 = go.Scatter(
    x=x,
    y=df_1[measure].tolist(),
    name='Semester 1  ',
    text=None,
    textfont={'size': 14,
              'color': df_1.iloc[0]['colour_html']},
    line=go.Line(width=2,
                 color=df_1.iloc[0]['colour_html'],
                 dash=sem1_text,),
    marker=go.Marker(
      color=df_1.iloc[0]['colour_html'],
      size=8,
      symbol='circle'
    ),
    connectgaps=False,
    mode='lines+markers',
    showlegend=True,
    textposition='bottom right'
  )
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
    y=df_targets['gts_target'].tolist(),
    name='Target',
    text=df_targets['gts_target'].tolist(),
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
  
  fig = {'data': traces,
         'layout': go.Layout(
           title=graph_title,
           titlefont={'size': 20,},
           showlegend=True,
           legend=dict(
             font=dict(size=14),
             orientation="h",
           ),
           xaxis=dict(
             range=[0, no_terms],
             tickvals=x,
             tickfont={'size': 16},
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
             titlefont={'size': 18},
             range=[68, 88],
             tickvals=[70, 72.5, 75, 77.5, 80, 82.5, 85, 87.5],
             ticktext=[70, '', 75, '', 80, '', 85, ''],
             ticklen=5,
             tickfont={'size': 16},
             zeroline=True,
             zerolinewidth=2,
           ),
           width=width,
           height=height,
           hovermode='closest',
           margin=dict(b=40, l=60, r=5, t=40),
           hidesources=True,
         )
         }
  filename = folder + '{}_{}_{}_2018'.format(df_2.iloc[0]['school_name_short'], level, measure)
  plotly.offline.plot(fig, filename+'.html')
  py.image.save_as(fig, filename+'.png')
  return fig
  
'''
level = 'HE'
for school in ('ACCT', 'EFM', 'MGT', 'VBE', 'GSBL', 'BITL'):
  fig = line_graph_school_measure(
    df_schools_data,
    school,
    level=level,
    measure='gts',
    start_year=start_year,
    end_year=end_year,
    height=600,
    width=1100)

level = 'VE'
school = 'VBE'
fig = line_graph_school_measure(
  df_schools_data,
  school,
  level=level,
  measure='gts',
  start_year=start_year,
  end_year=end_year,
  height=600,
  width=1100)
'''

def line_trace_school_measure(df1,
                              school,
                              level='HE',
                              measure='gts',
                              start_year=2014, end_year=2018,
                              semester=None,
                              dash_type=None):
  
  df_school = df1.loc[df1['school_name_short'] == school]
  df_school = df_school.loc[df_school['level'] == level]
  
  if semester == 1:
    df_sem = df_school.loc[df1['semester'] == 1]
  elif semester == 2:
    df_sem = df_school.loc[df1['semester'] == 2]
  
  x = [i - 0.5 for i in range(1, int(end_year) - int(start_year) + 2)]
  
  colour = df_sem.iloc[0]['colour_html']
  
  print(school, colour)
  # Create Semester trace (solid)
  trace = go.Scatter(
    x=x,
    y=df_sem[measure].tolist(),
    name='<span style="color: {2}">{0} ({1})   </span>'.format(school, level, colour),
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


def create_school_RMIT_graph(
  df1,
  measure='gts',
  start_year=2015, end_year=2018,
  semester=1,
  folder='H:\\Projects\\CoB\\CES\\School Reporting\\2018 S2\\',
  height=600,
  width=1100,
  background='#000000'):
  
  if background == '#000000':
    line_col = '#FFFFFF'
  else:
    line_col = None
  
  traces = []
  x = [i + 0.5 for i in range(0, (int(end_year) - int(start_year) + 1))]
  xlabels = ['{}'.format(i) for i in range(int(start_year), int(end_year) + 1)]

  graph_title = '<b>CES (Semester {1}):</b> CoB {0} by School'.format(measure.upper(), semester)
  
  for school in [['ACCT', 'HE'],
                 ['BITL', 'HE'],
                 ['EFM', 'HE'],
                 ['GSBL', 'HE'],
                 ['MGT', 'HE'],
                 ['VBE', 'HE'],
                 ['VBE', 'VE']]:
    
    if school[1] == 'VE':
      dash_type = 'dot'
    else:
      dash_type = None
    
    traces.append(line_trace_school_measure(
      df1,
      school[0],
      level=school[1],
      measure='gts',
      start_year=start_year, end_year=end_year,
      semester=semester,
      dash_type=dash_type))
  
  fig = go.Figure(
    data=traces,
    layout=go.Layout(
      title=graph_title,
      titlefont={'size': 16, },
      showlegend=True,
      legend=dict(
        font=dict(size=12),
        orientation="h",
        bgcolor=background
      ),
      paper_bgcolor=background,
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
        range=[68, 88],
        tickvals=[70, 72.5, 75, 77.5, 80, 82.5, 85, 87.5],
        ticktext=[70, '', 75, '', 80, '', 85, ''],
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
  filename = folder + 'CoB_schools_{}_{}S{}'.format(measure, end_year, semester)
  plotly.offline.plot(fig, filename + '.html')
  py.image.save_as(fig, filename+'.png')
  return fig


fig = create_school_RMIT_graph(
  df1=df_schools_data,
  measure='gts',
  start_year=2015, end_year=2018,
  semester=2,
  folder='H:\\Projects\\CoB\\CES\\School Reporting\\2018 S2\\',
  height=400,
  width=800,
  background='#FFFFFF')
