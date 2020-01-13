import plotly
from tabulate import tabulate
import plotly.graph_objs as go
import plotly.offline


from tabulate import tabulate
import pandas as pd
import numpy as np

import scipy.stats as scipystats
from statsmodels.graphics.regressionplots import *
import matplotlib.pyplot as plt

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc


from general.db_helper_functions import (
  db_extract_query_to_dataframe
)

def create_ce_comparison_chart(cur, width=800, height=600, display=False, save=False, start_year=2017, end_year=2019,
                               show_title=True,
                               show_annotations=True,
                               show_ylabel=True,
                               show_pval=True,
                               table='vw204_ce_evaluation'
                               ):
  qry = " SELECT year, semester, course_code_ces, gts_delta::numeric, " \
        "  CASE WHEN la=true THEN 1 ELSE 0 END AS ce" \
        "	FROM course_enhancement.{} \n" \
        " WHERE gts_pre IS NOT NULL AND gts_post IS NOT NULL \n" \
        "   AND year >= {} AND year <= {} \n" \
        "".format(table,
                  start_year, end_year)
  
  df1 = db_extract_query_to_dataframe(qry, cur, print_messages=False)
  df1['gts_delta'] = df1['gts_delta'].astype(float)
  
  df1_group = df1.groupby(["year", "semester", "ce"])
  #print(df1_group.gts_delta.agg([np.mean, np.std, scipystats.sem, len]))
  pval = []
  ms_mean = []
  nms_mean = []
  ms_sem = []
  nms_sem = []
  labels = []
  
  for sem in [[2017, 1], [2017, 2], [2018, 1], [2018, 2], [2019, 1], [2019, 2]]:
    df_temp1 = df1.query('ce==1 & year=={} & semester=={}'.format(sem[0], sem[1]))
    df_temp2 = df1.query('ce==0 & year=={} & semester=={}'.format(sem[0], sem[1]))
    if show_pval == True:
      pval.append(scipystats.ttest_ind(df_temp1.gts_delta, df_temp2.gts_delta)[1])
      labels.append('{} S{}<br>'
                    'p-val={}'.format(sem[0], sem[1],
                                      '%.3f' % scipystats.ttest_ind(df_temp1.gts_delta, df_temp2.gts_delta)[1]))
      xtick_size = 14
    else:
      labels.append('{} S{}'.format(sem[0], sem[1]))
      xtick_size = 10
    ms_mean.append(np.mean(df_temp1.gts_delta))
    nms_mean.append(np.mean(df_temp2.gts_delta))
    ms_sem.append(scipystats.sem(df_temp1.gts_delta))
    nms_sem.append(scipystats.sem(df_temp2.gts_delta))
  
  print(ms_mean)
  print(nms_mean)
  print(pval)
  #print(labels)

  trace1 = go.Bar(
    x=labels,
    y=nms_mean,
    text=['%.1f' % val for val in nms_mean],
    textposition='outside',
    name='Other',
    marker=dict(
      color=rc.RMIT_Red),
    error_y=dict(
      type='data',
      array=nms_sem,
      visible=True,
      color=rc.RMIT_Green
    )
  )
  trace2 = go.Bar(
    x=labels,
    y=ms_mean,
    text=['%.2f' % val for val in ms_mean],
    textposition='outside',
    name='Enhanced',
    marker=dict(
      color=rc.RMIT_Black),
    error_y=dict(
      type='data',
      array=ms_sem,
      visible=True,
      color=rc.RMIT_Green
    )
  )
  
  data = [trace2, trace1]
  
  if show_title == True:
    title='Mean Change in Course GTS'
  else:
    title = None
  
  if show_ylabel == True:
    ylabel = 'Change in GTS'
  else:
    ylabel = None
  
  
  layout = go.Layout(
    title=title,
    titlefont=dict(size=24),
    showlegend=True,
    width=width,
    height=height,
    margin=dict(b=20, l=20, r=10, t=10),
    hidesources=True,
    xaxis=dict(
      tickfont=dict(
        size=xtick_size,
      )
    ),
    plot_bgcolor=rc.RMIT_White,
    yaxis=dict(
      title=ylabel,
      titlefont=dict(
        size=16,)
      ),
    legend=dict(
      orientation="v",
      x=0.6,
      y=0.95)
  )
  
  if show_annotations == True:
    annotations = [dict(x=0.6,
                        y=1,
                        text='The "Change in course GTS" is between:<br>'
                             '  1. The average GTS of the two previous offerings of the course; and<br>'
                             '  2. The average GTS of the labeled and next offering of the course<br>'
                             ' There is no next offering data for 2019 S1',
                        font=dict(size=12),
                        xref='paper',
                        yref='paper',
                        showarrow=False
                        ),
                   ]
    layout['annotations'] = annotations
    
  fig = go.Figure(data=data, layout=layout)
  
  if display == True:
    plotly.offline.plot(
            fig,
            filename='H:\\Projects\\CoB\\CES\\Course Enhancement\\CE_vs_NCE_2019S2.html'
            )
  if save == True:
    plotly.plotly.image.save_as(
      fig,
      filename='H:\\Projects\\CoB\\CES\\Course Enhancement\\CE_vs_NCE_2019S2.png'
    )
  return fig


def create_ce_growth(cur, width=800, height=600, start_year=2017, end_year=2019,
                     show_title=True,
                     show_annotations=True,
                     show_ylabel=True
                     ):
  qry = " SELECT year, semester, count(DISTINCT course_code_ces) AS count \n " \
        " FROM course_enhancement.tbl_courses \n " \
        " WHERE " \
        "     cob_engagement = True \n" \
        "      AND level != 'VN' \n" \
        "      AND year >= {} AND year <= {}" \
        " GROUP BY  year, semester \n" \
        "".format(start_year, end_year)
  
  df1 = db_extract_query_to_dataframe(qry, cur, print_messages=False)
  
  labels = []
  for sem in [[2017, 1], [2017, 2], [2018, 1], [2018, 2], [2019, 1], [2019, 2]]:
    labels.append('{} S{}'.format(sem[0], sem[1]))

  trace1 = go.Bar(
    x=labels,
    y=df1['count'],
    name='No. of Courses',
    textposition='inside',
    marker=dict(
      color=rc.RMIT_Black),
  )
  data = [trace1]
  
  if show_title == True:
    title = 'Growth in Course Enhancement'
  else:
    title = None
  
  if show_ylabel == True:
    ylabel = 'Change in GTS'
  else:
    ylabel = None
  
  layout = go.Layout(
    title=title,
    titlefont=dict(size=24),
    showlegend=True,
    width=width,
    height=height,
    margin=dict(b=20, l=25, r=10, t=10),
    hidesources=True,
    xaxis=dict(
      tickfont=dict(
        size=10,
      )
    ),
    plot_bgcolor=rc.RMIT_White,
    yaxis=dict(
      title=ylabel,
      titlefont=dict(
        size=16, )
    ),
    legend=dict(
      orientation="v",
      x=0.01,
      y=0.90)
  )
  
  if show_annotations == True:
    annotations = [dict(x=0.6,
                        y=1,
                        text='The "Change in course GTS" is between:<br>'
                             '  1. The average GTS of the two previous offerings of the course; and<br>'
                             '  2. The average GTS of the labeled and next offering of the course<br>'
                             ' There is no next offering data for 2019 S1',
                        font=dict(size=12),
                        xref='paper',
                        yref='paper',
                        showarrow=False
                        ),
                   ]
    layout['annotations'] = annotations
  
  fig = go.Figure(data=data, layout=layout)
  
  return fig