import RMIT_colours as rc

import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools
import plotly.offline

import sys
sys.path.append('C:\\Peter\\CoB\\python_scripts')

from tabulate import tabulate
import pandas as pd
import numpy as np
import itertools
import statsmodels.formula.api as smf
import scipy.stats as scipystats
import statsmodels.api as sm
import statsmodels.stats.stattools as stools
import statsmodels.stats as stats
from statsmodels.graphics.regressionplots import *
import matplotlib.pyplot as plt
import seaborn as sns
import copy
import math
import time



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
con, cur = connect_to_postgres_db(con_string)

'''--------------------------------- Initialise Parameters  ----------------------------'''
start_year = '2014'
end_year = '2018'


qry = " SELECT year, semester, course_code, gts_delta::numeric, CASE WHEN ms=true THEN 1 ELSE 0 END AS ms \n" \
      "	FROM projects.vw_pre_post_offerings_delta_ms \n" \
      " WHERE gts_pre IS NOT NULL AND gts_post IS NOT NULL \n" \

df1 = db_extract_query_to_dataframe(qry, cur, print_messages=False)
df1['gts_delta'] = df1['gts_delta'].astype(float)


df1_group = df1.groupby(["year", "semester", "ms"])
print(df1_group.gts_delta.agg([np.mean, np.std, scipystats.sem]))
pval = []
ms_mean = []
nms_mean = []
ms_sem = []
nms_sem = []
labels = []

for sem in [[2016, 2], [2017, 1], [2017, 2], [2018, 1]]:
  df_temp1 = df1.query('ms==1 & year=={} & semester=={}'.format(sem[0], sem[1]))
  df_temp2 = df1.query('ms==0 & year=={} & semester=={}'.format(sem[0], sem[1]))
  pval.append(scipystats.ttest_ind(df_temp1.gts_delta, df_temp2.gts_delta)[1])
  labels.append('{} S{}<br>'
                'p-val={}'.format(sem[0], sem[1],
                                  '%.3f' % scipystats.ttest_ind(df_temp1.gts_delta, df_temp2.gts_delta)[1]))
  ms_mean.append(np.mean(df_temp1.gts_delta))
  nms_mean.append(np.mean(df_temp2.gts_delta))
  ms_sem.append(scipystats.sem(df_temp1.gts_delta))
  nms_sem.append(scipystats.sem(df_temp2.gts_delta))

print(pval)
print(labels)
x = [i for i in range(len(pval))]
trace1 = go.Bar(
  x=labels,
  y=nms_mean,
  text=['%.2f' % val for val in nms_mean],
  textposition='top center',
  name='No Microsurgery',
  marker=dict(
    color=rc.RMIT_DarkBlue),
  error_y=dict(
    type='data',
    array=nms_sem,
    visible=True,
    color=rc.RMIT_Red
  )
)
trace2 = go.Bar(
  x=labels,
  y=ms_mean,
  text=['%.2f' % val for val in ms_mean],
  textposition='outside center',
  name='Microsurgery',
  marker=dict(
    color=rc.RMIT_Green),
  error_y=dict(
    type='data',
    array=ms_sem,
    visible=True,
    color=rc.RMIT_Red
  )
)

data = [trace1, trace2]

layout = go.Layout(
  title='Average "Change in Course GTS" for CoB',
  titlefont=dict(size=24),
  showlegend=True,
  width=800,
  height=600,
  margin=dict(b=35, l=40, r=0, t=50),
  hidesources=True,
  xaxis=dict(
    tickfont=dict(
      size=14,
    )
  ),
  yaxis=dict(
    title='Change in GTS',
    titlefont=dict(
      size=16,)
    ),
  legend=dict(
    orientation="v",
    x=0.01,
    y=1)
)

annotations = [dict(x=0.6,
                    y=1,
                    text='The "Change in course GTS" is between:<br>'
                         '  1. The average GTS of the two previous offerings of the course; and<br>'
                         '  2. The average GTS of the labeled and next offering of the course<br>'
                         ' There is no next offering data for 2018 S1',
                    font=dict(size=12),
                    xref='paper',
                    yref='paper',
                    showarrow=False
                    ),
               
               ]
layout['annotations'] = annotations
    
fig = go.Figure(data=data, layout=layout)

plotly.offline.plot(
        fig,
        filename='C:\\Peter\\CoB\\CES\\Microsurgeries\\MS_vs_NMS.html'
        )
plotly.plotly.image.save_as(
  fig,
  filename='C:\\Peter\\CoB\\CES\\Microsurgeries\\MS_vs_NMS.png'
)

def create_improve_bar(x, y, width, height, maxy=90):
  bar = go.Bar(
    x=x,
    y=y,
    text=y,
    textposition='outside',
    marker=dict(
      color=[rc.RMIT_DarkBlue, rc.RMIT_Green]),
  )
  
  layout = go.Layout(
    title=None,
    showlegend=False,
    xaxis=dict(
      tickvals=None,
      showgrid=False,
      ticktext=None,
      showticklabels=False,
      ticks='',
      zeroline=False),
    yaxis=dict(
      range=[0, maxy],
      tickvals=None,
      showgrid=False,
      showticklabels=False,
      ticks='',
      zeroline=False),
    width=width,
    height=height,
    margin=dict(b=0, l=10, r=0, t=10),
    hidesources=True,
  )
  return go.Figure(data=[bar], layout=layout)
'''
df1_ = df1.copy()
reg = smf.ols(formula="gts_post ~ ms + gts_pre",
              data=df1_).fit()
reg.summary()
print(reg.summary())

df1_['pred'] = reg.predict()

plt.scatter(df1_.query('ms == 0').gts_pre, df1_.query('ms == 0').pred, c="b", marker="o")
plt.scatter(df1_.query('ms == 1').gts_pre, df1_.query('ms == 1').pred, c="r", marker="+")
plt.plot()
plt.show()

plt.scatter(df1_.query('ms == 0').gts_pre, df1_.query('ms == 0').gts_post, c="b", marker="o")
plt.scatter(df1_.query('ms == 1').gts_pre, df1_.query('ms == 1').gts_post, c="r", marker="+")
plt.plot()
plt.show()

plt.scatter(df1_.query('ms == 0').gts_pre, df1_.query('ms == 0').gts_delta, c="b", marker="o")
plt.scatter(df1_.query('ms == 1').gts_pre, df1_.query('ms == 1').gts_delta, c="r", marker="+")
plt.plot()
plt.show()

print('\n\n\n')
lm_0 = smf.ols(formula = "gts_post ~ gts_pre", data = df1.query('ms == 0')).fit()
print(lm_0.summary())
plt.scatter(df1.query('ms == 0').gts_pre.values, df1.query('ms == 0').gts_post.values, label="actual")
plt.scatter(df1.query('ms == 0').gts_pre.values, lm_0.predict(), c="r", label="predict")
plt.legend()
plt.show()

print('\n\n\n')
lm_1 = smf.ols(formula = "gts_post ~ gts_pre", data = df1.query('ms == 1')).fit()
print(lm_1.summary())
plt.scatter(df1.query('ms == 1').gts_pre.values, df1.query('ms == 1').gts_post.values, label="actual")
plt.scatter(df1.query('ms == 1').gts_pre.values, lm_1.predict(), c="r", label="predict")
plt.legend()
plt.show()

print('\n\n\n')
yrxsome_df1 = df1
yrxsome_df1["yrxsome"] = yrxsome_df1.ms * yrxsome_df1.gts_pre

lm = smf.ols("gts_post ~ gts_pre + ms + yrxsome", data = yrxsome_df1).fit()
print(lm.summary())


plt.scatter(yrxsome_df1.query('ms == 0').gts_pre, lm.predict()[yrxsome_df1.ms.values == 0], marker="+")
plt.scatter(yrxsome_df1.query('ms == 1').gts_pre, lm.predict()[yrxsome_df1.ms.values == 1], c="r", marker="x")
plt.scatter(yrxsome_df1.query('ms == 0').gts_pre, yrxsome_df1.query('ms == 0').gts_post, c = "black", marker = "*")
plt.scatter(yrxsome_df1.query('ms == 1').gts_pre, yrxsome_df1.query('ms == 1').gts_post, c = "r", marker = "d")
plt.plot()
plt.show()
'''