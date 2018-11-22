import RMIT_colours as rc
import plotly
import sys

from tabulate import tabulate

import plotly.graph_objs as go
import pandas as pd
import decimal
import psycopg2
import traceback

from tabulate import tabulate

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc


from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe,
  convert_list_string_for_sql
)


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


def qry_vw_changes(schema='ces_responses', table='vw_changes_2'):
  qry = " SELECT \n" \
        "   course_code, intervention, \n" \
        "   course_count_2017, course_count_2018, \n" \
        "   invites_2017, invites_2018, \n" \
        "   w1_2017_r, w1_2018_r, \n" \
        "   w2_2017_r, w2_2018_r, \n" \
        "   w3_2017_r, w3_2018_r, \n" \
        "   w4_2017_r, w4_2018_r, \n" \
        "   w5_2017_r, w5_2018_r, \n" \
        "   w1_2017_rr, w1_2018_rr, \n" \
        "   w2_2017_rr, w2_2018_rr, \n" \
        "   w3_2017_rr, w3_2018_rr, \n" \
        "   w4_2017_rr, w4_2018_rr, \n"\
        "   w5_2017_rr, w5_2018_rr, \n" \
        "   w1_drr, w2_drr, w3_drr, w4_drr , w5_drr  \n" \
        " FROM {0}.{1}; \n" \
        "".format(schema,
                  table)
  return(qry)

'''--------------------------------- Plotting functions  ----------------------------'''
def graphRRline(df1):
  df_w1 = df1.loc[df['intervention'] == 'week1']
  df_nw1 = df1.loc[df['intervention'] != 'week1']

  # all traces for plotly
  traces = []

  for i, r in df_w1.iterrows():
    # check for valid colour value
    j = i
    while j > len(colourList)-1:
      j = j-len(colourList)
    edge_trace=go.Scatter(
      x=[1, 2],
      y=[r['w1_drr'], r['w2_drr']],
      text="%s" % r['course_code'],
      line=go.Line(width=2, color=colourList[j]),
      hoverinfo=r['course_code'],
      connectgaps=False,
      mode='lines+markers',
      showlegend=False)
    traces.append(edge_trace)

  title = 'CES course response rate'
  title += '<br>'
  title += '{} '.format('Intervention in Week 1')

  fig = {'data': traces,
         'layout': go.Layout(
           title=title,
           showlegend=True,
           xaxis=dict(
             title='Week',
             range=[0.5, 2.5],
             autotick=False,
             ticks='outside',
             tick0=1,
             dtick=1,
             ticklen=5,
             zeroline=False,
           ),
           yaxis=dict(
             title='Change in response rate (2017-2018)',
             ticklen=5,
             zeroline=True,
             zerolinewidth=4,
           ),
           width=1200,
           height=800,
           hovermode='closest',
           margin=dict(b=50, l=50, r=50, t=50),
           hidesources=True,
         )
         }

  plotly.offline.plot(fig, filename='C:\\Peter\\CoB\\CES Response Rates\\rr.html')
  return fig

def graphRRbar(df1):
  df_w1 = df1

  # all traces for plotly
  traces = []

  for i, r in df_w1.iterrows():
    trace_2017 = go.Bar(
      x=['End of Week 1', 'End of Week 2', 'End of Week3'],
      y=[r['w1_2017_rr'], r['w2_2017_rr'],  r['w3_2017_rr']],
      text=['{} courses'.format(r['course_count_2017']),
            '{} courses'.format(r['course_count_2017']),
            '{} courses'.format(r['course_count_2017'])],
      textposition='bottom',
      marker=dict(
        color = rc.RMIT_Green,
      ),
      name='2017 CES'
    )
    trace_2018 = go.Bar(
      x=['End of Week 1', 'End of Week 2', 'End of Week3'],
      y=[r['w1_2018_rr'], r['w2_2018_rr'], r['w3_2018_rr']],
      text=['{} courses'.format(r['course_count_2018']),
            '{} courses'.format(r['course_count_2018']),
            '{} courses'.format(r['course_count_2018'])],
      textposition='bottom',
      marker=dict(
        color=rc.RMIT_Blue,
      ),
      name='2018 CES'
    )
    
    data = [trace_2017, trace_2018]

    title = 'CES response rates <br>'
    if r['intervention'] == 'No':
      title = 'CES response rates <br>' \
              'for courses that were NOT visited'.format(r['intervention'])

    if r['intervention'] == 'Any':
      title = 'CES response rates <br>' \
              'for courses that were visited'.format(r['intervention'])
    
    #title += '{} '.format('Intervention in Week 1')
    
    layout = go.Layout(
      title=title,
      showlegend=True,
      barmode='group',
      yaxis=dict(
        title='Response rate',
        range=[0,40],
        ticklen=5),
      width=1200,
      height=800,
      hovermode='closest',
      margin=dict(b=50, l=50, r=50, t=50),
      hidesources=True,
    )
    
    fig = {'data': data,
           'layout': layout,
           }

    plotly.offline.plot(fig, filename='C:\\Peter\\CoB\\CES Response Rates\\graphs\\rr_{}.html'.format(r['intervention']))
  return


def graphDRRbar(df1):
  df_no = df1.loc[df1['intervention'] == 'No']
  df_any = df1.loc[df1['intervention'] == 'Any']
  
  # all traces for plotly
  traces = []

  for i, r in df_no.iterrows():
    trace1 = go.Bar(
      x=['End of Week 1', 'End of Week 2', 'End of Week3', 'End of Week4',  'End of Week5'],
      y=[r['w1_drr'], r['w2_drr'], r['w3_drr'], r['w4_drr'], r['w5_drr']],
      hovertext=[
        '    {} courses not visited<br>'
        ' 2017:  {} response rate<br>'
        ' 2018:  {} response rate'.format(
          r['course_count_2018'],
          r['w1_2017_rr'],
          r['w1_2018_rr']),
        '    {} courses not visited<br>'
        ' 2017:  {} response rate<br>'
        ' 2018:  {} response rate'.format(
          r['course_count_2018'],
          r['w2_2017_rr'],
          r['w2_2018_rr']),
        '    {} courses not visited<br>'
        ' 2017:  {} response rate<br>'
        ' 2018:  {} response rate'.format(
          r['course_count_2018'],
          r['w3_2017_rr'],
          r['w3_2018_rr']),
        '    {} courses not visited<br>'
        ' 2017:  {} response rate<br>'
        ' 2018:  {} response rate'.format(
          r['course_count_2018'],
          r['w4_2017_rr'],
          r['w4_2018_rr']),
        '    {} courses not visited<br>'
        ' 2017:  {} response rate<br>'
        ' 2018:  {} response rate'.format(
          r['course_count_2018'],
          r['w5_2017_rr'],
          r['w5_2018_rr']),
      ],
      text=[r['w1_drr'], r['w2_drr'], r['w3_drr'], r['w4_drr'], r['w5_drr']],
      textposition='outside',
      hoverinfo='hovertext',
      marker=dict(
        color=rc.RMIT_Blue,
      ),
      name='Non DropIn Courses'
    )

  for i, r in df_any.iterrows():
    trace2 = go.Bar(
      x=['End of Week 1', 'End of Week 2', 'End of Week3', 'End of Week4', 'End of Week5'],
      y=[r['w1_drr'], r['w2_drr'], r['w3_drr'], r['w4_drr'], r['w5_drr']],
      hovertext=[
        '    {} courses visited<br>'
        ' 2017:  {} response rate<br>'
        ' 2018:  {} response rate'.format(
          r['course_count_2018'],
          r['w1_2017_rr'],
          r['w1_2018_rr']),
        '    {} courses visited<br>'
        ' 2017:  {} response rate<br>'
        ' 2018:  {} response rate'.format(
          r['course_count_2018'],
          r['w2_2017_rr'],
          r['w2_2018_rr']),
        '    {} courses visited<br>'
        ' 2017:  {} response rate<br>'
        ' 2018:  {} response rate'.format(
          r['course_count_2018'],
          r['w3_2017_rr'],
          r['w3_2018_rr']),
        '    {} courses visited<br>'
        ' 2017:  {} response rate<br>'
        ' 2018:  {} response rate'.format(
          r['course_count_2018'],
          r['w4_2017_rr'],
          r['w4_2018_rr']),
        '    {} courses visited<br>'
        ' 2017:  {} response rate<br>'
        ' 2018:  {} response rate'.format(
          r['course_count_2018'],
          r['w5_2017_rr'],
          r['w5_2018_rr']),
      ],
      text=[r['w1_drr'], r['w2_drr'], r['w3_drr'], r['w4_drr'], r['w5_drr']],
      textposition='outside',
      hoverinfo='hovertext',
      marker=dict(
        color=rc.RMIT_Green,
      ),
      name='DropIn Courses'
    )
  data = [trace1, trace2]
  
  title = 'CES - Difference between 2017 and 2018 % response rate<br>' \
          '  Effectiveness of the DropIn campaign'
  
  layout = go.Layout(
      title=title,
      showlegend=True,
      barmode='group',
      yaxis=dict(
        title='Change in % response rate',
        ticklen=5),
      width=1200,
      height=800,
      hovermode='closest',
      margin=dict(b=50, l=50, r=50, t=50),
      hidesources=True,
    )
    
  fig = {'data': data,
         'layout': layout,
         }
    
  plotly.offline.plot(fig,
                      filename='C:\\Peter\\CoB\\CES Response Rates\\graphs\\rdr.html')
  return



#qry1 = qry_vw_changes(schema='ces_responses', table='vw_changes_2')

#df_courses = db_extract_query_to_dataframe(qry1, cur, print_messages=False)
qry2 = qry_vw_changes(schema='ces_responses', table='vw_agg_changes')
df_all = db_extract_query_to_dataframe(qry2, cur, print_messages=False)

print(qry2)

#print(tabulate(df_courses, headers='keys'))
#print(tabulate(df_courses, headers='keys'))
print('\n\n')
print(qry2)
print(tabulate(df_all, headers='keys'))

#fig = graphRRbar(df_all)
fig = graphDRRbar(df_all)

















