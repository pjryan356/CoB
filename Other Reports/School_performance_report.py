import plotly
import plotly.graph_objs as go
import plotly.offline
import numpy as np
import scipy.stats as scipystats
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
#postgres_pw = input("Postgres Password: ")
#postgres_user = 'pjryan'
#postgres_host = 'localhost'
#postgres_dbname = 'postgres'

#con_string = "host='{0}' " \
#             "dbname='{1}' " \
#             "user='{2}' " \
#             "password='{3}' " \
#             "".format(postgres_host, postgres_dbname, postgres_user, postgres_pw)
#postgres_con, postgres_cur = connect_to_postgres_db(con_string)

'''-------------------------------------------- Get Data -------------------------------------'''
def get_school_data(start_year, postgres_cur):
  qry = ' SELECT * \n' \
        ' FROM ces.vw146_school_bus_for_graph \n' \
        "   WHERE year >= {}" \
        " ORDER BY school_code, level, year, semester" \
        "; \n".format(start_year)

  return db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)
  
#df_schools_data = get_school_data(start_year, postgres_cur)

def line_graph_school_measure(df1, school, level='HE', measure='gts',
                              start_year=2015, end_year=2019,
                              height=400,
                              width=800,
                              show_targets=True):
  df_school = df1.loc[df1['school_name_short'] == school]
  df_targets = df_school[['year', 'gts_target']].drop_duplicates()
  df_school = df_school.loc[df_school['level'] == level]
  
  df_1 = df_school.loc[df_school['semester'] == 1]
  df_2 = df_school.loc[df_school['semester'] == 2]
  
  # print(tabulate(df_school, headers='keys'))
  # print(tabulate(df_targets, headers='keys'))
  # print(end_year)
  
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
  sem1_text = [None for j in range(len(x) - 1)]
  sem1_text.append(df_1.iloc[-1][measure])
  #print(sem1_text)
  
  # Create Semester 1 trace (solid)
  trace_sem1 = go.Scatter(
    x=x,
    y=df_1[measure].tolist(),
    name='Semester 1  ',
    text=None,
    textfont={'size': 14,
              'color': df_1.iloc[0]['colour_html']},
    line=go.scatter.Line(
      width=2,
      color=df_1.iloc[0]['colour_html'],
      dash=sem1_text, ),
    marker=go.scatter.Marker(
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

  # Create Semester 2 trace (dashed)
  trace_sem2 = go.Scatter(
    x=x,
    y=df_2[measure].tolist(),
    name='Semester 2  ',
    text=None,
    line=go.scatter.Line(
      width=2,
      color=df_2.iloc[0]['colour_html'],
      dash='dot', ),
    marker=go.scatter.Marker(
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
  
  if show_targets == True and measure == 'gts':
    trace_target = go.Scatter(
      x=x,
      y=df_targets['gts_target'].tolist(),
      name='Target',
      text=df_targets['gts_target'].tolist(),
      textfont={'size': 14,
                'color': rc.RMIT_Black},
      line=go.scatter.Line(width=2, color=rc.RMIT_Black),
      marker=go.scatter.Marker(
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
           titlefont={'size': 20, },
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
  
  if show_targets == True and measure == 'gts':
    filename = folder + '{}_{}_{}_2018_targets'.format(df_2.iloc[0]['school_name_short'], level, measure)
  plotly.offline.plot(fig, filename + '.html')
  py.image.save_as(fig, filename + '.png')
  return fig


def line_trace_school_measure(df1,
                              school,
                              level='HE',
                              measure='gts',
                              start_year=2014, end_year=2018,
                              semester=None,
                              dash_type=None,
                              line_color=None,
                              df_cob=None):
  df_school = df1.loc[df1['school_name_short'] == school]
  if level != 'All':
    df_school = df_school.loc[df_school['level'] == level]
  else:
    df_school = df_school.loc[df_school['level'] == 'NA']
  
  #print(tabulate(df_school, headers='keys'))
  
  if semester == 1:
    df_sem = df_school.loc[df1['semester'] == 1]
  elif semester == 2:
    df_sem = df_school.loc[df1['semester'] == 2]
  #print(tabulate(df_sem, headers='keys'))
  
  x = [i - 0.5 for i in range(1, int(end_year) - int(start_year) + 2)]
  
  if line_color != None:
    colour = line_color
  else:
    try: colour = df_sem.iloc[0]['colour_html']
    except: pass
  
  #print(len(df_sem))
  
  if len(df_sem) == 0 and school == 'CoB':
    colour = rc.RMIT_Black
    if semester == 1:
      df_sem = df_cob.loc[df_cob['semester'] == 1]
    elif semester == 2:
      df_sem = df_cob.loc[df_cob['semester'] == 2]
    
    #print(df_sem)
    
  if school in ['VBE', 'CoB']:
    name = '<span style="color: {0}">{1} ({2})</span>'.format(colour, school, level)
  else:
    name = '<span style="color: {0}">{1}</span>'.format(colour, school)

  #print(school, colour, name)
  
  # Create Semester trace (solid)
  trace = go.Scatter(
    x=x,
    y=df_sem[measure].tolist(),
    name=name,
    text=None,
    textfont={'size': 14,
              'color': colour},
    line=go.scatter.Line(
      width=3,
      color=colour,
      dash=dash_type),
    marker=go.scatter.Marker(
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


def line_trace_school_course_mean_measure(
  df1,
  school,
  level='HE',
  measure='gts',
  start_year=2014, end_year=2019,
  semester=None,
  dash_type=None,
  line_color=None,
  df_cob=None,
  xoffset=0,
  err=False):
  
  
  df_school = df1.loc[df1['school_name_short'] == school]
  
  if school == 'CoB':
    df_school = df1
    
  if level != 'All':
    df_school = df_school.loc[df_school['level'] == level]
  else:
    df_school = df_school.loc[df_school['level'] == 'NA']

  if semester == 1:
    df_sem = df_school.loc[df1['semester'] == 1]
  elif semester == 2:
    df_sem = df_school.loc[df1['semester'] == 2]
  # print(tabulate(df_sem, headers='keys'))
  
  x = [i - 0.5 + xoffset for i in range(1, int(end_year) - int(start_year) + 2)]
  
  if line_color != None:
    if school == 'CoB':
      colour = line_color
    
  else:
    try:
      colour = df_sem.iloc[0]['colour_html']
      if school == 'CoB':
        colour = '#000000'
    except:
      pass

  # print(len(df_sem))

  
  if school in ['VBE', 'CoB']:
    name = '<span style="color: {0}">{1} ({2})</span>'.format(colour, school, level)
  else:
    name = '<span style="color: {0}">{1}</span>'.format(colour, school)

  # print(school, colour, name)
  means=[]
  errs=[]
  for yr in range(start_year, end_year + 1):
    df_sem.loc[df_sem['year'] == yr]
    means.append(np.mean(df_sem.loc[df_sem['year'] == yr][measure]))
    errs.append(scipystats.sem(df_sem.loc[df_sem['year'] == yr][measure]))
    
  if err==False:
    errs=None
  # Create Semester trace (solid)
  trace = go.Scatter(
    x=x,
    y=means,
    name=name,
    text=None,
    textfont={'size': 14,
              'color': colour},
    line=go.scatter.Line(
      width=3,
      color=colour,
      dash=dash_type),
    marker=go.scatter.Marker(
      color=colour,
      size=8,
      symbol='diamond'
    ),
    error_y=dict(
      type='data',
      array=errs,
      visible=True,
      color=colour),
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
  height=600,
  width=1100,
  background='#000000',
  df_cob=None,
  school=None,
  mean=False):
  
  if background == '#000000':
    line_col = '#FFFFFF'
  else:
    line_col = None
  
  if mean:
    ytitle = 'Mean'
    yrange = [3.6, 4.4]
    ytickvals = [3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4]
    yticktext = [3.6, '', 3.8, '', 4.0, '', 4.2, '', 4.4]

  else:
    ytitle = 'Percent Agree'
    yrange = [68, 88]
    ytickvals = [70, 72.5, 75, 77.5, 80, 82.5, 85, 87.5]
    yticktext = [70, '', 75, '', 80, '', 85, '']

  traces = []
  x = [i + 0.5 for i in range(0, (int(end_year) - int(start_year) + 1))]
  xlabels = ['{}'.format(i) for i in range(int(start_year), int(end_year) + 1)]
  
  if school == None:
    school_list = [['ACCT', 'HE'],
                   ['BITL', 'HE'],
                   ['EFM', 'HE'],
                   ['GSBL', 'HE'],
                   ['MGT', 'HE'],
                   ['VBE', 'HE'],
                   ['VBE', 'VE'],
                   ['CoB', 'HE'],
                   ]
  elif school == 'VBE':
    school_list = [['VBE', 'HE'],
                   ['VBE', 'VE'],
                   ['CoB', 'HE'],
                   ]
  else:
    school_list = [[school, 'HE'],
                   ['CoB', 'HE'],
                   ]
  
  for school in school_list:
    
    if school[1] == 'VE':
      dash_type = 'dot'
    else:
      dash_type = None
    
    traces.append(line_trace_school_measure(
      df1,
      school[0],
      level=school[1],
      measure=measure,
      start_year=start_year, end_year=end_year,
      semester=semester,
      dash_type=dash_type,
      df_cob=df_cob))
  
  fig = go.Figure(
    data=traces,
    layout=go.Layout(
      title=None,
      showlegend=False,
      legend=dict(
        font=dict(size=10),
        orientation="h",
        bgcolor=background
      ),
      paper_bgcolor=background,
      plot_bgcolor=background,
      xaxis=dict(
        title=None,
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
        title=ytitle,
        range=yrange,
        tickvals=ytickvals,
        ticktext=yticktext,
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
      margin=dict(b=25, l=60, r=10, t=20),
      hidesources=True,
    )
  )
  return fig

def create_school_course_mean_graph(
  df1,
  measure='gts',
  start_year=2015, end_year=2018,
  semester=1,
  height=600,
  width=1100,
  df_cob=None,
  err=False,
  xoffset=False):
  
  df1[measure] = df1[measure].astype(float)
  
  x = [i + 0.5 for i in range(0, (int(end_year) - int(start_year) + 1))]
  xlabels = ['{}'.format(i) for i in range(int(start_year), int(end_year) + 1)]
  
  traces = []
  offset = -0.09
  for school in [['ACCT', 'HE'],
                 ['BITL', 'HE'],
                 ['EFM', 'HE'],
                 ['GSBL', 'HE'],
                 ['MGT', 'HE'],
                 ['VBE', 'HE'],
                 ['VBE', 'VE'],
                 ['CoB', 'HE'],
                 ]:
    
    offset += 0.02
    
    if xoffset == False:
      offset=0
    
    if school[1] == 'VE':
      dash_type = 'dot'
    else:
      dash_type = None
    
    traces.append(line_trace_school_course_mean_measure(
      df1,
      school[0],
      level=school[1],
      measure=measure,
      start_year=start_year, end_year=end_year,
      semester=semester,
      dash_type=dash_type,
      df_cob=df_cob,
      xoffset=offset,
      err=err))

  fig = go.Figure(
    data=traces,
    layout=go.Layout(
      title=False,
      showlegend=False,
      legend=dict(
        font=dict(size=10),
        orientation="h",
      ),
      xaxis=dict(
        title=False,
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
        range=[68, 88],
        tickvals=[70, 72.5, 75, 77.5, 80, 82.5, 85, 87.5],
        ticktext=[70, '', 75, '', 80, '', 85, ''],
        ticklen=5,
        tickfont={'size': 12},
        zeroline=True,
        zerolinewidth=2,
        gridcolor=None,
        layer="below traces",
      ),
      width=width,
      height=height,
      hovermode='closest',
      margin=dict(b=25, l=60, r=10, t=20),
      hidesources=True,
    )
  )
  return fig

def create_CoB_graph(
  df1,
  measure='gts',
  start_year=2015, end_year=2018,
  semester=1,
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
  
  for school in [
                 ['CoB', 'HE'],
                 ['CoB', 'VE'],
                 ['CoB', 'All'],
                 ]:
    
    if school[1] == 'All':
      color=rc.RMIT_Red
    else:
      color=None
    
    if school[1] == 'VE':
      dash_type = 'dot'
    else:
      dash_type = None
    
    #print(school, color)
    
    traces.append(line_trace_school_measure(
      df1,
      school[0],
      level=school[1],
      measure=measure,
      start_year=start_year, end_year=end_year,
      semester=semester,
      dash_type=dash_type,
      line_color=color)
    )
  
  fig = go.Figure(
    data=traces,
    layout=go.Layout(
      title='CoB CES {} (Semester 1)'.format(measure.upper()),
      showlegend=True,
      legend=dict(
        font=dict(size=10),
        orientation="h",
        bgcolor=background
      ),
      paper_bgcolor=background,
      plot_bgcolor=background,
      xaxis=dict(
        title=False,
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
      margin=dict(b=25, l=60, r=10, t=40),
      hidesources=True,
    )
  )

  filename = 'H:\\Projects\\CoB\\CES\\School Reporting\\2019 S1\\' + 'CoB_{}_2019S1'.format(measure)
  plotly.offline.plot(fig, filename + '.html')
  py.image.save_as(fig, filename + '.png')
  return fig


#print(tabulate(df_schools_data, headers='keys'))
measure='osi'
semester=2
graph_title = '<b>CES (Semester {1}):</b> CoB {0} by School'.format(measure.upper(), semester)



'''
fig = create_school_RMIT_graph(
  df1=df_schools_data,
  measure=measure,
  start_year=2015, end_year=2018,
  semester=semester,
  folder='H:\\Projects\\CoB\\CES\\School Reporting\\2018 S2\\',
  height=400,
  width=800,
  background='#FFFFFF',
  graph_title=graph_title)



level = 'HE'
for school in ('ACCT', 'EFM', 'MGT', 'GSBL', 'BITL'):
  fig = line_graph_school_measure(
    df_schools_data,
    school,
    level='HE',
    measure='gts',
    start_year=start_year,
    end_year=end_year,
    height=600,
    width=1100,
    show_targets=False)


school = 'VBE'
for level in ['HE', 'VE']:
  fig = line_graph_school_measure(
    df_schools_data,
    school,
    level=level,
    measure='gts',
    start_year=start_year,
    end_year=end_year,
    height=600,
    width=1100,
    show_targets=False
  )
'''