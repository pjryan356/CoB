

import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc
from tabulate import tabulate

import plotly.offline



from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
)



'''--------------------------------- Initialise Parameters  ----------------------------'''

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
 
def qry_location_history(location,
                         course_name,
                         degree_type="('UG')",
                         schema='projects',
                         table='tbl_common_core_fr_cleaned'):
  
  qry = ' SELECT year, semester, location, course_name, fail_rate \n' \
        ' FROM {0}.{1} \n' \
        " WHERE degree_type IN {2} \n" \
        "   AND location = '{3}' \n" \
        "   AND course_name = '{4}' \n" \
        "".format(schema, table, degree_type, location, course_name)
  
  qry += " ORDER BY course_name, location, year, semester\n"
  return qry

def qry_location_diff_history(course_name):
  qry = " SELECT \n" \
        "   year, semester, course_name, \n" \
        "   sum(fail_rate) FILTER (WHERE location = 'SIM') AS fr_sim, \n" \
        "   sum(fail_rate) FILTER (WHERE location = 'ONSHORE') AS fr_onshore, \n" \
        "   sum(fail_rate) FILTER (WHERE location = 'ONSHORE') - \n" \
        "   sum(fail_rate) FILTER (WHERE location = 'SIM') AS fr_diff \n" \
        " FROM projects.tbl_common_core_fr_cleaned \n" \
        " WHERE degree_type = 'UG' AND semester <> 3 AND course_name = '{}' \n" \
        " GROUP BY year, semester, course_name \n" \
        " ORDER BY course_name, year, semester \n" \
        "".format(course_name)
  
  return qry


def qry_course_history(course_name,
                       location=None,
                       degree_type=None,
                       schema='projects',
                       table='tbl_common_core_fr_cleaned'):
  qry = ' SELECT year, semester, location, course_name, fail_rate \n' \
        ' FROM {0}.{1} \n' \
        " WHERE course_name = '{2}'".format(schema, table, course_name)

  if location != None:
      qry += "   AND degree_type IN {} \n".format(degree_type)
  if location != None:
      qry += "   AND location = '{}' \n".format(location)
  qry += " ORDER BY course_name, location, year, semester\n"
  return qry

def line_trace_course_fr(course_name,
                         colour,
                         location=None,
                         degree_type=None,
                         semester=None,
                         dash_type=None,
                         show_course_name=True,
                         showlegend=True
                         ):
  qry = qry_course_history(
    location=location,
    course_name=course_name,
    degree_type=degree_type)
  
  df1 = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)
  if semester == 1:   df1 = df1.loc[df1['semester'] == 1]
  elif semester == 2: df1 = df1.loc[df1['semester'] == 2]
  
  x = [i/2.0 for i in range(1, 7)]
  
  if location == 'VIETNAM':
    x = []
    for j in range(0,2):
      for i in range(0,3):
        x.append(j+0.5+i/4.0)
  
  if show_course_name == True:
    label = '<span style="color: {0}">{2} ({1})   </span>'.format(colour, location, course_name)
  else:
    label = '<span style="color: {0}">{1}   </span>'.format(colour, location)
  # Create Semester 1 trace (solid)
  trace = go.Scatter(
    x=x,
    y=df1['fail_rate'].tolist(),
    name=label,
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
    connectgaps=True,
    mode='lines+markers',
    showlegend=showlegend,
    textposition='bottom right'
  )
  return trace


def line_trace_course_fr_diff(course_name,
                              colour,
                              semester=None,
                              dash_type=None,
                              showlegend=True):
  qry = qry_location_diff_history(course_name)
  df1 = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)
  if semester == 1:
    df1 = df1.loc[df1['semester'] == 1]
  elif semester == 2:
    df1 = df1.loc[df1['semester'] == 2]
  
  x = [i - 0.5 for i in range(1, 7)]
  
  # Create Semester 1 trace (solid)
  trace = go.Scatter(
    x=x,
    y=df1['fr_diff'].tolist(),
    name='<span style="color: {1}"> {0} </span>'.format(course_name, colour),
    text=None,
    textfont={'size': 14,
              'color': colour},
    line=go.Line(width=3,
                 color=colour,
                 dash=dash_type),
    marker=go.Marker(
      color=colour,
      size=10,
      symbol='diamond'
    ),
    connectgaps=False,
    mode='markers',
    showlegend=showlegend,
    textposition='bottom right',
  )
  return trace

def create_location_course_graph(
  location='ONSHORE',
  semester=None,
  folder='C:\\Peter\\CoB\\CES\\2018_Semester_1\\',
  height=600,
  width=1100,
  background='#000000'):
  
  traces = []
  x = [i - 0.5 for i in range(1, 6)]
  xlabels = ['2016 S1', '2016 S2', '2017 S1', '2017 S2', '2018 S1']
  #graph_title = 'School {} (% Agree) by year (Semester {})'.format(measure.upper(), semester)
  graph_title = 'Common Core Fail Rate: {} (UG)'.format(location)
  cList = ['Accounting in Orgs & Society',
           'Business Computing 1',
           'Business Statistics 1',
           'Commercial Law',
           'Introduction to Management',
           'Macroeconomics 1',
           'Marketing Principles',
           'Prices & Markets']
  colourList = [
    rc.RMIT_Red,
    rc.RMIT_White,
    rc.RMIT_Green,
    rc.RMIT_Arctic,
    rc.RMIT_Lemon,
    rc.RMIT_Orange,
    rc.RMIT_Teal,
    rc.RMIT_Lavender
  ]
  for i in range(len(cList)):
    colour = colourList[i]
    course_name = cList[i]
    
    traces.append(
      line_trace_course_fr(
        course_name,
        colour,
        location=location,
        degree_type="('UG')",
        semester=semester,
        dash_type=None
      )
    )
  print(traces)
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
        range=[0, 5],
        tickvals=x,
        tickfont={'size': 12},
        showgrid=False,
        ticktext=xlabels,
        ticks='outside',
        tick0=1,
        dtick=1,
        ticklen=5,
        zeroline=True,
        gridcolor='#FFFFFF',
        zerolinewidth=2,
           ),
      yaxis=dict(
        title='Fail Rate (%)',
        titlefont={'size': 14},
        range=[0, 25],
        ticklen=5,
        tickfont={'size': 12},
        zeroline=True,
        gridcolor='gray',
        zerolinewidth=2,
        layer="below traces",
      ),
      width=width,
      height=height,
      hovermode='closest',
      margin=dict(b=40, l=60, r=5, t=40),
      hidesources=True,
    )
  )
  filename = folder + 'common_core_{}_graph_UG'.format(location.lower())
  plotly.offline.plot(fig, filename+'.html')
  print (filename)
  return fig


def create_location_diff_course_graph(
  semester=None,
  folder='C:\\Peter\\CoB\\CES\\2018_Semester_1\\',
  height=600,
  width=1100,
  background='#000000'):
  
  traces = []
  x = [i - 0.5 for i in range(1, 6)]
  xlabels = ['2016 S1', '2016 S2', '2017 S1', '2017 S2', '2018 S1']
  # graph_title = 'School {} (% Agree) by year (Semester {})'.format(measure.upper(), semester)
  graph_title = 'Common Core: ONSHORE Fail Rate - SIM Fail Rate (UG)'
  cList = ['Accounting in Orgs & Society',
           'Business Computing 1',
           'Business Statistics 1',
           'Commercial Law',
           'Introduction to Management',
           'Macroeconomics 1',
           'Marketing Principles',
           'Prices & Markets']
  colourList = [
    rc.RMIT_Red,
    rc.RMIT_White,
    rc.RMIT_Green,
    rc.RMIT_Arctic,
    rc.RMIT_Lemon,
    rc.RMIT_Orange,
    rc.RMIT_Teal,
    rc.RMIT_Lavender
  ]
  for i in range(len(cList)):
    colour = colourList[i]
    course_name = cList[i]
  
    
    traces.append(
      line_trace_course_fr_diff(course_name,
                                colour,
                                semester=None,
                                dash_type=None)
    )
  
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
      paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor=background,
      xaxis=dict(
        range=[0, 5],
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
        title='Difference (Fail Rate %)',
        titlefont={'size': 14},
        range=[-5, 25],
        ticklen=5,
        tickfont={'size': 12},
        zeroline=True,
        gridcolor='gray',
        zerolinewidth=2,
        layer="below traces",
      ),
      width=width,
      height=height,
      hovermode='closest',
      margin=dict(b=40, l=60, r=5, t=40),
      hidesources=True,
    )
  )
  filename = folder + 'common_core_location_diff_graph_UG'.format()
  print(filename)
  plotly.offline.plot(fig, filename + '.html')
  return fig


def create_course_graph(
  course_name,
  degree,
  semester=None,
  folder='C:\\Peter\\CoB\\CES\\2018_Semester_1\\',
  height=600,
  width=1100):
  traces = []
  x = [i/2.0 for i in range(1, 6)]
  xlabels = ['2016 S1', '2016 S2', '2017 S1', '2017 S2', '2018 S1']
  # graph_title = 'School {} (% Agree) by year (Semester {})'.format(measure.upper(), semester)
  graph_title = '{} ({}) Fail Rate'.format(course_name, degree)

  colourList = [
    rc.RMIT_Green,
    rc.RMIT_DarkBlue,
    rc.RMIT_Red,
    rc.RMIT_Arctic
    ]
  
  qry = ' SELECT DISTINCT location \n' \
        ' FROM projects.tbl_common_core_fr_cleaned \n' \
        " WHERE degree_type = '{}' \n" \
        "       AND course_name = '{}' " \
        "       AND location <> 'UPH' \n" \
        "       AND location <> 'VIETNAM' \n" \
        ' ORDER BY location' \
        ''.format(degree, course_name)

  df_locs = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)
  
  for i, r in df_locs.iterrows():
    colour = colourList[i]
    location = r.location
    
    traces.append(
      line_trace_course_fr(
        course_name,
        colour,
        location=location,
        degree_type="('{}')".format(degree),
        semester=semester,
        dash_type=None,
        show_course_name=False
      )
    )
  fig = go.Figure(
    data=traces,
    layout=go.Layout(
      title=graph_title,
      titlefont={'size': 16, },
      showlegend=True,
      legend=dict(
        font=dict(size=12),
        orientation="h",
      ),
      xaxis=dict(
        range=[0, 5],
        tickvals=x,
        tickfont={'size': 12},
        showgrid=False,
        ticktext=xlabels,
        ticks='outside',
        tick0=1,
        dtick=1,
        ticklen=5,
        zeroline=True,
        gridcolor='#FFFFFF',
        zerolinewidth=2,
      ),
      yaxis=dict(
        title='Fail Rate (%)',
        titlefont={'size': 14},
        range=[0, 40],
        ticklen=5,
        tickfont={'size': 12},
        zeroline=True,
        zerolinewidth=2,
        layer="below traces",
      ),
      width=width,
      height=height,
      hovermode='closest',
      margin=dict(b=40, l=60, r=5, t=40),
      hidesources=True,
    )
  )
  filename = folder + '{}_{}_graph.html'.format(course_name.lower(), degree)
  plotly.offline.plot(fig, filename=filename)
  
  print(filename)
  return fig

cList = ['Accounting in Orgs & Society',
         'Business Computing 1',
         'Business Statistics 1',
         'Commercial Law',
         'Introduction to Management',
         'Macroeconomics 1',
         'Marketing Principles',
         'Prices & Markets']

degList = ['DIPCOM', 'UG']

for degree in degList:
  if degree == 'DIPCOM':
    ylim = [0, 36]
  else:
    ylim=[0, 22]
    
  sp_count = -1 # used to keep track of subplots
  fig = tools.make_subplots(rows=4, cols=2, subplot_titles=cList,
                            horizontal_spacing=0.07, vertical_spacing=0.06,
                            shared_xaxes=False,
                            shared_yaxes=False)

  for course_name in cList:
    x = [i / 2.0 for i in range(1, 6)]
    xlabels = ['2016<br>S1', '2016<br>S2', '2017<br>S1', '2017<br>S2', '2018<br>S1']
    #Set up subplot parameteres
    sp_count += 1
    row = int(sp_count/2) + 1
    col = sp_count-(row-1)*2 + 1
    
    showlegend = False
    if col == 1 and row == 1:
      showlegend = True

    colourList = [
      rc.RMIT_Green,
      rc.RMIT_DarkBlue,
      rc.RMIT_Red,
      rc.RMIT_Arctic
    ]

    qry = ' SELECT DISTINCT location \n' \
          ' FROM projects.tbl_common_core_fr_cleaned \n' \
          " WHERE degree_type = '{}' \n" \
          "       AND course_name = '{}' " \
          "       AND location <> 'UPH' \n" \
          ' ORDER BY location' \
          ''.format(degree, course_name)

    df_locs = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)

    for i, r in df_locs.iterrows():
      colour = colourList[i]
      location = r.location

      fig.append_trace(
        line_trace_course_fr(
          course_name,
          colour,
          location=location,
          degree_type="('{}')".format(degree),
          semester=None,
          dash_type=None,
          show_course_name=False,
          showlegend=showlegend),
        row,
        col)
   
    print(course_name)
    print (row, col)
    x_axis = 'xaxis{}'.format(sp_count + 1)
    if row == 4:
      fig['layout'][x_axis].update(
        tickvals=x,
        tickfont={'size': 10},
        showgrid=False,
        ticktext=xlabels,
        range=[0.25, 2.75]
      )
    
    else:
      fig['layout'][x_axis].update(
        tickvals=x,
        showticklabels=False,
        tickfont={'size': 10},
        showgrid=False,
        ticktext='',
        range=[0.25, 2.75])
    
    y_axis='yaxis{}'.format(sp_count + 1)
    
    if col == 1:
      fig['layout'][y_axis].update(
        title='Fail Rate (%)',
        titlefont=dict(
          size=12),
      )

    fig['layout'][y_axis].update(range=ylim)
  
  fig['layout'].update(
    height=1000,
    width=700,
    title='Common Core ({}) Fail Rates'.format(degree),
    titlefont=dict(
      size=16),
    margin=dict(b=30, l=40, r=5, t=90),
    legend=dict(
      font=dict(size=10),
      orientation="h",
      x=0,
      y=1.05
    )
  )
  for j in fig['layout']['annotations']:
    j['font'] = dict(size=12)
    
  folder = 'C:\\Peter\\'
  filename = folder + 'CC_{}_graph.html'.format(degree)
  plotly.offline.plot(fig, filename=filename)
  

'''
create_location_course_graph(
  location='ONSHORE',
  semester=None,
  folder='C:\\Peter\\CoB\\Request\\Jason\\',
  height=400,
  width=800)

create_location_course_graph(
  location='SIM',
  semester=None,
  folder='C:\\Peter\\CoB\\Request\\Jason\\',
  height=400,
  width=800)

create_location_diff_course_graph(
  semester=None,
  folder='C:\\Peter\\CoB\\Request\\Jason\\',
  height=400,
  width=800)
'''