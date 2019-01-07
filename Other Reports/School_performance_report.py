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

school = 'ACCT'
acad_career = 'HE'
start_year = '2015'
end_year = '2019'


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
      " WHERE school_name_short ='{0}' " \
      "   AND year >= {2}" \
      "; \n".format(school, acad_career, start_year)
 
df_school = db_extract_query_to_dataframe(qry, postgres_cur, print_messages=False)

print(tabulate(df_school, headers='keys'))

if acad_career == 'HE':
  gts_list = ['The teaching staff are extremely good at explaining things (*SEi)',
              'The teaching staff normally give me helpful feedback on how I am going in this course (**PE)',
              'The teaching staff motivate me to do my best work (SEi)',
              'The teaching staff work hard to make this course interesting (SEi)',
              'The teaching staff make a real effort to understand difficulties I might be having in this course (PE)',
              'The teaching staff put a lot of time into commenting on my work (PE)',
              '\*SEi: Student Engagement (impact);\u00A0\u00A0\*\*PE: Perceived Effort;']
  
elif acad_career == 'VE':
  gts_list = ['My instructors have a thorough knowledge of the course assessment (PC)*',
              'My instructors provide opportunities to ask questions (SEp)**',
              'My instructors treat me with respect (SEp)',
              'My instructors understand my learning needs (PC)',
              'My instructors communicate the course content effectively (SEi)***',
              'My instructors make the course content as interesting as possible (SEi)',
              '\*PC: Perceived Capability;\u00A0\u00A0\*\*SEp: Student Engagement (practice);\u00A0\u00A0\*\*\*SEi: Student Engagement (impact);']


def line_graph_school_measure(df1, school_name, measure='gts',
                              start_year=2015, end_year=2018,
                              height=400,
                              width=800):
  df_1 = df1.loc[df1['semester'] == 1]
  df_2 = df1.loc[df1['semester'] == 2]
  df_targets = df1[['year', 'gts_target']].drop_duplicates()
  
  # all traces for plotly
  traces = []
  xlabels = []
  
  for year in range(int(start_year), int(end_year) + 1):
    xlabels.append('{}<br>'.format(year))
  
  no_terms = len(xlabels)
  
  x = [i - 0.5 for i in range(1, no_terms + 1)]
  
  label_check = 0

  graph_title = '<b>{1}:</b> CES School {0} and targets'.format(measure.upper(), school_name)
  
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
  filename = folder + '{}_{}_2018'.format(df_2.iloc[0]['school_name_short'], measure)
  plotly.offline.plot(fig, filename+'.html')
  py.image.save_as(fig, filename+'.png')
  return fig

fig = line_graph_school_measure(
                df_school, df_school.iloc[0]['school_name'],
                measure='gts',
                start_year=start_year, end_year=end_year,
                height=600,
                width=1100)


