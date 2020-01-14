import plotly
import chart_studio.plotly as py
from tabulate import tabulate
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import traceback
import dash_html_components as html

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc

from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
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

postgres_con, postgres_cur = connect_to_postgres_db(con_string)

def get_data(cur, tbl, schema='ces'):
  # Returns a dataframe with CES data for courses in course list
  qry = ' SELECT *\n' \
        ' FROM {0}.{1} \n' \
        "".format(schema, tbl)
  return db_extract_query_to_dataframe(qry, cur, print_messages=False)

df_teacher = get_data(postgres_cur, tbl='vw8501_teacher_efm_clean')
df_course = get_data(postgres_cur, tbl='vw8511_course_efm_clean')


fig = (px.line(df.loc[df['Survey'] == 'Graduate Satisfaction'],
               x='Year',
               y='Percent Agree',
               facet_col="Level",
               color='Metric',
               line_dash="Value",
               color_discrete_map={'OSI': rc.RMIT_DarkBlue,
                                   'GTS': rc.RMIT_Red,
                                   'GSS': rc.RMIT_Green,
                                   'FTE': rc.RMIT_DarkBlue,
                                   'FFS': rc.RMIT_Red,
                                   'EF': rc.RMIT_Green},

               width=1140, height=320
               )
       .update_xaxes(range=[2015.5, 2019.5],
                     tickvals=[2016, 2017, 2018, 2019],
                     ticks='outside',
                     title=None)
       .update_traces(mode='lines+markers',
                      )
       )

fig.for_each_trace(
    lambda trace: trace.update(name=trace.name.replace("Metric=", "")),
)

fig.for_each_trace(
    lambda trace: trace.update(name=trace.name.replace(", Value=FY", "")),
)

fig.for_each_trace(
    lambda trace: trace.update(name=trace.name.replace(", Value=", " ")),
)

fig.update_layout(
  title=dict(text='CoB Graduate Student Satisfaction',
             xref='container',
             x=0.45,
             yref='container',),
  yaxis=dict(
    range=[55, 90],
  ),
  margin=dict(b=30, l=55, r=5, t=55))

fig.write_image('H:\\Projects\\CoB\\GOS\\Student_satisfaction' + '.png')

fig.show()

fig2 = (px.line(df.loc[df['Survey'] == 'Graduate Outcomes'],
                x='Year',
                y='Percent Agree',
                facet_col="Level",
                color='Metric',
                line_dash="Value",
                color_discrete_map={'OSI': rc.RMIT_DarkBlue,
                                    'GTS': rc.RMIT_Red,
                                    'GSS': rc.RMIT_Green,
                                    'FTE': rc.RMIT_DarkBlue,
                                    'FFS': rc.RMIT_Red,
                                    'EF': rc.RMIT_Green},

                width=1140, height=320
                )
        .update_xaxes(range=[2015.5, 2019.5],
                      tickvals=[2016, 2017, 2018, 2019],
                      ticks='outside',
                      title=None)
        .update_traces(mode='lines+markers',
                       )
        )

fig2.for_each_trace(
    lambda trace: trace.update(name=trace.name.replace("Metric=", "")),
)

fig2.for_each_trace(
    lambda trace: trace.update(name=trace.name.replace(", Value=FY", "")),
)

fig2.for_each_trace(
    lambda trace: trace.update(name=trace.name.replace(", Value=", " ")),
)

fig2.update_layout(
  title=dict(text='CoB Graduate Employment Outcomes',
             xref='container',
             x=0.5,
             yref='container',),
  yaxis=dict(
    range=[0, 90],
  ),
  margin=dict(b=30, l=55, r=135, t=55))

fig2.write_image('H:\\Projects\\CoB\\GOS\\Employment_Outcomes' + '.png')

fig2.show()

