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

data = [
    ['HE', 'Graduate Satisfaction', 'GSS', 'FY', 2016, 80.4],
    ['HE', 'Graduate Satisfaction', 'OSI', 'FY', 2016, 78.3],
    ['HE', 'Graduate Satisfaction', 'GTS', 'FY', 2016, 61.6],
    ['HE', 'Graduate Outcomes', 'FTE', 'FY', 2016, 68.2],
    ['HE', 'Graduate Outcomes', 'FFS', 'FY', 2016, 18.5],
    ['HE', 'Graduate Outcomes', 'EF', 'FY', 2016, 5.7],
  
    ['HE', 'Graduate Satisfaction', 'OSI', 'FY', 2017, 77.2],
    ['HE', 'Graduate Satisfaction', 'GTS', 'FY', 2017, 61.5],
    ['HE', 'Graduate Satisfaction', 'GSS', 'FY', 2017, 77.9],
    ['HE', 'Graduate Outcomes', 'FTE', 'FY', 2017, 73],
    ['HE', 'Graduate Outcomes', 'FFS', 'FY', 2017, 21],
    ['HE', 'Graduate Outcomes', 'EF', 'FY', 2017, 4.1],

    ['HE', 'Graduate Satisfaction', 'OSI', 'FY', 2018, 78.8],
    ['HE', 'Graduate Satisfaction', 'GTS', 'FY', 2018, 62.8],
    ['HE', 'Graduate Satisfaction', 'GSS', 'FY', 2018, 78.7],
    ['HE', 'Graduate Outcomes', 'FTE', 'FY', 2018, 71.8],
    ['HE', 'Graduate Outcomes', 'FFS', 'FY', 2018, 19.7],
    ['HE', 'Graduate Outcomes', 'EF', 'FY', 2018, 3.1],

    ['VE', 'Graduate Satisfaction', 'OSI', 'FY', 2016, 82.9],
    ['VE', 'Graduate Satisfaction', 'GTS', 'FY', 2016, 82.5],
    ['VE', 'Graduate Satisfaction', 'GSS', 'FY', 2016, 74.1],
    ['VE', 'Graduate Outcomes', 'FTE', 'FY', 2016, 65.8],
    ['VE', 'Graduate Outcomes', 'FFS', 'FY', 2016, 58.0],
    ['VE', 'Graduate Outcomes', 'EF', 'FY', 2016, 13.0],
  
    ['VE', 'Graduate Satisfaction', 'OSI', 'FY', 2017, 83.7],
    ['VE', 'Graduate Satisfaction', 'GTS', 'FY', 2017, 84.3],
    ['VE', 'Graduate Satisfaction', 'GSS', 'FY', 2017, 76.3],
    ['VE', 'Graduate Outcomes', 'FTE', 'FY', 2017, 62.3],
    ['VE', 'Graduate Outcomes', 'FFS', 'FY', 2017, 60.0],
    ['VE', 'Graduate Outcomes', 'EF', 'FY', 2017, 8.6],
    
    ['VE', 'Graduate Satisfaction', 'OSI', 'FY', 2018, 86.5],
    ['VE', 'Graduate Satisfaction', 'GTS', 'FY', 2018, 83.7],
    ['VE', 'Graduate Satisfaction', 'GSS', 'FY', 2018, 78.8],
    ['VE', 'Graduate Outcomes', 'FTE', 'FY', 2018, 68.8],
    ['VE', 'Graduate Outcomes', 'FFS', 'FY', 2018, 50.7],
    ['VE', 'Graduate Outcomes', 'EF', 'FY', 2018, 3.5],
  
  ['HE', 'Graduate Satisfaction', 'OSI', 'Target', 2018, 78.8],
  ['HE', 'Graduate Satisfaction', 'OSI', 'Target', 2019, 80.6],
  ['HE', 'Graduate Satisfaction', 'GTS', 'Target', 2018, 62.8],
  ['HE', 'Graduate Satisfaction', 'GTS', 'Target', 2019, 62.5],
  
  ['VE', 'Graduate Satisfaction', 'OSI', 'Target', 2018, 86.5],
  ['VE', 'Graduate Satisfaction', 'OSI', 'Target', 2019, 87.0],
  ['VE', 'Graduate Satisfaction', 'GTS', 'Target', 2018, 83.7],
  ['VE', 'Graduate Satisfaction', 'GTS', 'Target', 2019, 85.2],
]

df = pd.DataFrame(data, columns=['Level', 'Survey', 'Metric', 'Value', 'Year', 'Percent Agree'])

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

