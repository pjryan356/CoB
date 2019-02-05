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

college_short = 'SEH'
acad_career = 'VE'
start_year = '2015'
end_year = '2018'


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
      ' FROM ces.vw156_college_for_graph \n' \
      " WHERE year >= {1} AND level = '{0}'" \
      "; \n".format(acad_career, start_year)
 
df_college = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)

print(tabulate(df_college, headers='keys'))


def line_graph_college_measure(df1, college_name_short, measure='gts',
                              start_year=2015, end_year=2018,
                              height=400,
                              width=800):
  df_1 = df1.loc[(df1['semester'] == 1) & (df1['college_name_short'] == college_name_short)]
  df_2 = df1.loc[(df1['semester'] == 2) & (df1['college_name_short'] == college_name_short)]
  
  # all traces for plotly
  traces = []
  xlabels = []
  
  for year in range(int(start_year), int(end_year) + 1):
    xlabels.append('{}<br>'.format(year))
  
  no_terms = len(xlabels)
  
  x = [i - 0.5 for i in range(1, no_terms + 1)]
  
  label_check = 0

  graph_title = '<b>{1}:</b> CES College {0}'.format(measure.upper(), college_name_short)
  
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
      symbol='cirle'
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
             range=[59, 91],
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
  filename = folder + '{}_{}_2018'.format(df_2.iloc[0]['college_name_short'], measure)
  plotly.offline.plot(fig, filename+'.html')
  py.image.save_as(fig, filename+'.png')
  return fig


def line_graph_colleges_measure(df1, level, measure='gts',
                               start_year=2015, end_year=2018,
                               height=400,
                               width=800):
  
  # all traces for plotly
  traces = []
  xlabels = []
  yrange = [67, 89]
  yticks = [68, 72, 76, 80, 84, 88]
  ytitle = 'Percent Agree'
  
  
  if 'mean' in measure:
    yrange = [3.7, 4.5]
    yticks = [3.8, 4.0, 4.2, 4.4]
    if 'gts' in measure:
      ytitle = 'Mean GTS (0-5)'
    if 'osi' in measure:
      ytitle = 'Mean OSI (0-5)'
    
  for year in range(int(start_year), int(end_year) + 1):
    xlabels.append('{}<br>'.format(year))
  
  no_terms = len(xlabels)
  
  x = [i - 0.5 for i in range(1, no_terms + 1)]
  
  label_check = 0
  
  graph_title = 'CES College {0} ({1})'.format(measure.upper(), level)
  
  data_label = []
  y = []
  label_check += 1
  
  for college_name_short in ['CoB', 'DSC', 'SEH']:
    df_1 = df1.loc[(df1['semester'] == 1) & (df1['college_name_short'] == college_name_short)]
    df_2 = df1.loc[(df1['semester'] == 2) & (df1['college_name_short'] == college_name_short)]
  
    # Create Semester 1 trace (solid)
    trace_sem1 = go.Scatter(
      x=x,
      y=df_1[measure].tolist(),
      name='{} S1  '.format(college_name_short),
      text=None,
      textfont={'size': 14,
                'color': df_1.iloc[0]['colour_html']},
      line=go.Line(width=2,
                   color=df_1.iloc[0]['colour_html'],
                   ),
      marker=go.Marker(
        color=df_1.iloc[0]['colour_html'],
        size=8,
        symbol='cirle'
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
      name='{} S2  '.format(college_name_short),
      text=None,
      line=go.Line(width=2,
                   color=df_2.iloc[0]['colour_html'],
                   dash='dot', ),
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
             title=ytitle,
             titlefont={'size': 18},
             range=yrange,
             tickvals=yticks,
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
  filename = folder + '{}_{}_{}_2018'.format(acad_career, 'Colleges', measure)
  plotly.offline.plot(fig, filename + '.html')
  py.image.save_as(fig, filename + '.png')
  return fig
fig = line_graph_colleges_measure(
                df_college,
                acad_career,
                measure='gts_mean',
                start_year=start_year, end_year=end_year,
                height=600,
                width=1100)


fig = line_graph_colleges_measure(
                df_college,
                acad_career,
                measure='osi_mean',
                start_year=start_year, end_year=end_year,
                height=600,
                width=1100)