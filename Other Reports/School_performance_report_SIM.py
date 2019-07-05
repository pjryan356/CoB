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

folder = 'H:\\Projects\\CoB\\CES\\SIM\\2019\\School_summary\\'

start_year = 2017
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
      ' FROM sim_ces.vw302_school_bus_for_graph \n' \
      "   WHERE year >= {}" \
      " ORDER BY school, year, semester, staff_type" \
      "; \n".format(start_year)

df_schools_data = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)

print(tabulate(df_schools_data, headers='keys'))

'''-------------------------------------------- Functions ------------------------------------'''
def get_colour(measure):
  if measure == 'course_satisfaction':
    return rc.RMIT_Green
  if measure == 'lecturer_effectiveness':
    return rc.RMIT_DarkBlue
  if measure == 'subject_content':
    return rc.RMIT_Red
  return rc.RMIT_Black


def get_name(measure):
  if measure == 'course_satisfaction':
    return 'Course Satisfaction'
  if measure == 'lecturer_effectiveness':
    return 'Lecturer Effectiveness'
  if measure == 'subject_content':
    return 'Subject Content'
  return rc.RMIT_Black


def get_symbol(staff_type):
  if staff_type == 'RMIT':
    return 'diamond'
  if staff_type == 'Local':
    return 'x'
  return 'circle'


def get_dash(staff_type):
  if staff_type == 'RMIT':
    return None
  if staff_type == 'Local':
    return 'dash'
  return 'dot'


def line_graph_school_measure_sim(df1, school, measures=['subject_content'],
                                  start_year=2017, end_year=2019,
                                  height=400,
                                  width=800):
  f_df = df1.loc[df1['school'] == school]
  print(tabulate(f_df, headers='keys'))
  print('\n')
  
  # all traces for plotly
  traces = []
  xlabels = []

  for year in range(int(start_year), int(end_year) + 1):
    xlabels.append('{}<br> S1'.format(year))
    xlabels.append('{}<br> S2'.format(year))
    semesters = [1, 2]

  no_terms = len(xlabels)
  
  x = [i - 0.5 for i in range(1, no_terms + 1)]
  

  graph_title = '<b>{0}: </b>'.format(school)
  graph_title += 'SIM Data'

  
  # traces
  for measure in measures:
    #graph_title += '{}, '.format(get_name(measure))
    for staff_type in ['Local', 'RMIT']:
      data_label = []
      y = []

      for year in range(int(start_year), int(end_year) + 1):
        for sem in semesters:
          try:
            val = f_df.loc[(f_df['year'] == int(year)) & (f_df['semester'] == int(sem)) & (
              f_df['staff_type'] == staff_type)]

            val = val.iloc[0][measure]
            #print(school, year, sem, staff_type, measure, val)

          except:
            val = None
          y.append(val)

      trace = go.Scatter(
        x=x,
        y=y,
        name='{} ({})'.format(get_name(measure), staff_type),
        text=data_label,
        line=go.Line(
          width=2,
          color=get_colour(measure),
          dash=get_dash(staff_type)),
        marker=go.Marker(
          color=get_colour(measure),
          size=8,
          symbol=get_symbol(staff_type)
        ),
        connectgaps=True,
        mode='lines+markers',
        showlegend=True,
        textposition='top center'
      )
      traces.append(trace)

  #graph_title = graph_title[:-2]

  title = graph_title
  fig = go.Figure(
    data=traces,
    layout=go.Layout(
      title=title,
      showlegend=True,
      xaxis=dict(
        range=[0, no_terms],
        tickvals=x,
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
        title='Mean value',
        range=[3.75, 4.25],
        tickvals=[3.8, 3.85, 3.9, 3.95, 4.0, 4.05, 4.1, 4.15, 4.2],
        ticktext=[3.8, '', 3.9, '', 4.0, '', 4.1, '', 4.2, '', 4.3],
        ticklen=5,
        zeroline=True,
        zerolinewidth=2,
      ),
      width=width,
      height=height,
      hovermode='closest',
      margin=dict(b=40, l=50, r=5, t=40),
      hidesources=True,
    )
  )
  
  filename = folder + '{}_SIM_2019S1'.format(school)
  
  plotly.offline.plot(fig, filename + '.html')
  py.image.save_as(fig, filename + '.png')
  return fig



for school in ['ACCT', 'BITL', 'EFM', 'GSBL', 'MGT']:
  print('\n')

  fig = line_graph_school_measure_sim(
      df_schools_data,
      school,
      measures=['course_satisfaction', 'lecturer_effectiveness', 'subject_content'],
      start_year=start_year,
      end_year=end_year,
      height=600,
      width=1100)







'''
fig = create_school_RMIT_graph(
  df1=df_schools_data,
  measure='gts',
  start_year=2015, end_year=2018,
  semester=2,
  folder='H:\\Projects\\CoB\\CES\\School Reporting\\2018 S2\\',
  height=400,
  width=800,
  background='#FFFFFF')
'''