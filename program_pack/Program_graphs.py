import plotly
from tabulate import tabulate
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import traceback
import dash_html_components as html

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc

colourList = [rc.RMIT_Red,
              rc.RMIT_Green,
              rc.RMIT_Blue,
              rc.RMIT_Orange,
              rc.RMIT_Purple,
              rc.RMIT_Yellow,
              rc.RMIT_DarkBlue,
              rc.RMIT_Pink,
              rc.RMIT_Black,
              rc.RMIT_Aqua,
              rc.RMIT_Lemon,
              rc.RMIT_Lavender,
              rc.RMIT_Azure,
              rc.RMIT_Teal,
              rc.RMIT_Arctic
              ]

def line_graph_crse_prg(df_crse_ces,
                        df_crse_prg_ces,
                        course_code,
                        program_code,
                        measure='gts',
                        start_year=2014,
                        end_year=2018,
                        semester=None,
                        width=520, height=320):
  
  f_df_crse_ces = df_crse_ces.loc[df_crse_ces['course_code'] == course_code]
  f_df_crse_prg_ces = df_crse_prg_ces.loc[df_crse_prg_ces['course_code'] == course_code]
  
  # all traces for plotly
  traces = []
  xlabels = []
  
  for year in range(int(start_year), int(end_year) + 1):
    if semester == 1 or semester == 2:
      xlabels.append('{}<br> S{}'.format(year, semester))
      semesters = [semester]
    
    else:
      xlabels.append('{}<br> S1'.format(year))
      xlabels.append('{}<br> S2'.format(year))
      semesters = [1, 2]
  
  no_terms = len(xlabels)
  
  x = [i - 0.5 for i in range(1, no_terms + 1)]
  
  label_check = 0
  
  j = 0
  colours = [rc.RMIT_DarkBlue,
             rc.RMIT_Red]

  markers = ['circle',
             'diamond']
  
  sizes = [8, 8]
  

  label_check += 1
  names = ['{} (All)'.format(course_code),
           '{} ({})'.format(course_code, program_code)]
  for df in [f_df_crse_ces, f_df_crse_prg_ces]:
    
    y = []
    
    for year in range(int(start_year), int(end_year) + 1):
      for sem in semesters:
        try:
          val = df.loc[(df['year'] == year)
                       & (df['semester'] == sem)][measure].values[0]
        except:
          val = None
          
        y.append(val)
  
    trace = go.Scatter(
      x=x,
      y=y,
      name=names[j],
      line=go.scatter.Line(width=3, color=colours[j]),
      marker=go.scatter.Marker(
        color=colours[j],
        size=sizes[j],
        symbol=markers[j]
      ),
      connectgaps=True,
      mode='lines+markers',
      showlegend=False,
      textposition='top center'
    )
    traces.append(trace)
    j += 1
  
  title = '{1}({0}) vs {1}(All)'.format(program_code, course_code)
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
        title=' GTS Percent Agree',
        range=[19, 102],
        ticklen=5,
        zeroline=True,
        zerolinewidth=2,
      ),
      width=width,
      height=height,
      hovermode='closest',
      margin=dict(b=40, l=55, r=5, t=50),
      #hidesources=True,
    )
  )
  fig.layout.title = title
  return fig


def line_graph_prg_crses(df_prg_ces,
                         df_crse_prg_ces,
                         course_code,
                         program_code,
                         measure='gts',
                         start_year=2014,
                         end_year=2018,
                         semester=None,
                         width=520, height=320):
  
  f_df_crse_prg_ces = df_crse_prg_ces.loc[df_crse_prg_ces['course_code'] == course_code]
  
  # all traces for plotly
  traces = []
  xlabels = []
  
  for year in range(int(start_year), int(end_year) + 1):
    if semester == 1 or semester == 2:
      xlabels.append('{}<br> S{}'.format(year, semester))
      semesters = [semester]
    
    else:
      xlabels.append('{}<br> S1'.format(year))
      xlabels.append('{}<br> S2'.format(year))
      semesters = [1, 2]
  
  no_terms = len(xlabels)
  
  x = [i - 0.5 for i in range(1, no_terms + 1)]
  
  label_check = 0
  
  
  j = 0
  colours = [rc.RMIT_Blue,
             rc.RMIT_Red]
  
  markers = ['circle',
             'diamond']
  
  sizes = [8, 8]
  
  label_check += 1
  names = ['{}'.format(program_code),
           '{} ({})'.format(course_code, program_code)]
  
  
  # Add Individual courses

  for crse in df_crse_prg_ces.course_code.unique().tolist():
    
    df_temp = df_crse_prg_ces.loc[df_crse_prg_ces['course_code'] == crse]
    y = []

    for year in range(int(start_year), int(end_year) + 1):
      for sem in semesters:
        try:
          val = df_temp.loc[(df_temp['year'] == year)
                          & (df_temp['semester'] == sem)][measure].values[0]
      
        except:
          val = None
        y.append(val)
  
      trace = go.Scatter(
        x=x,
        y=y,
        line=go.scatter.Line(width=1, color=rc.RMIT_Grey1),
        connectgaps=True,
        mode='lines',
        showlegend=False,
        textposition='top center'
      )
      traces.append(trace)
    
  # Add overlaid plots (PRG, CRSE (PRG)
  for df in [df_prg_ces, f_df_crse_prg_ces]:
    
    y = []
    
    for year in range(int(start_year), int(end_year) + 1):
      for sem in semesters:
        try:
          val = df.loc[(df['year'] == year)
                       & (df['semester'] == sem)][measure].values[0]
        
        except:
          val = None
        y.append(val)
    
    trace = go.Scatter(
      x=x,
      y=y,
      name=names[j],
      line=go.scatter.Line(width=3, color=colours[j]),
      marker=go.scatter.Marker(
        color=colours[j],
        size=sizes[j],
        symbol=markers[j]
      ),
      connectgaps=True,
      mode='lines+markers',
      showlegend=False,
      textposition='top center'
    )
    traces.append(trace)
    j += 1
  
  title = '{1}({0}) vs {0} & Core Courses'.format(program_code, course_code)
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
        title='GTS Percent Agree',
        range=[19, 111],
        ticklen=5,
        zeroline=True,
        zerolinewidth=2,
      ),
      width=width,
      height=height,
      hovermode='closest',
      margin=dict(b=40, l=55, r=5, t=50),
      hidesources=True,
    )
  )
  
  return fig


def line_graph_crse_prg_enrol(df_crse_ces,
                              df_crse_prg_ces,
                              course_code,
                              program_code,
                              start_year=2014,
                              end_year=2018,
                              semester=None,
                              width=520, height=320):
  f_df_crse_ces = df_crse_ces.loc[df_crse_ces['course_code'] == course_code]
  f_df_crse_prg_ces = df_crse_prg_ces.loc[df_crse_prg_ces['course_code'] == course_code]
  
  # all traces for plotly
  traces = []
  xlabels = []
  
  for year in range(int(start_year), int(end_year) + 1):
    if semester == 1 or semester == 2:
      xlabels.append('{}<br> S{}'.format(year, semester))
      semesters = [semester]
    
    else:
      xlabels.append('{}<br> S1'.format(year))
      xlabels.append('{}<br> S2'.format(year))
      semesters = [1, 2]
  
  no_terms = len(xlabels)
  
  x = [i - 0.5 for i in range(1, no_terms + 1)]
  
  label_check = 0
  
  j = 0
  colours = [rc.RMIT_DarkBlue,
             rc.RMIT_Red,
             rc.RMIT_Red]
    
  label_check += 1
  names = ['Enrolments'.format(course_code),
           'Enrolments'.format(course_code, program_code),
           'Responses'.format(course_code, program_code)]
  
  # Add enrolments
  for df in [f_df_crse_ces, f_df_crse_prg_ces]:
    y = []
    for year in range(int(start_year), int(end_year) + 1):
      for sem in semesters:
        try:
          val = df.loc[(df['year'] == year)
                       & (df['semester'] == sem)]['population'].values[0]
        
        except:
          val = None
        
        y.append(val)
    
    trace = go.Scatter(
      x=x,
      y=y,
      name=names[j],
      line=go.scatter.Line(width=3, color=colours[j]),
      connectgaps=True,
      mode='lines',
      showlegend=True,
      textposition='top center'
    )
    traces.append(trace)
    j += 1

  #print(tabulate(f_df_crse_prg_ces, headers='keys'))
  for df in [f_df_crse_prg_ces]:
    y = []
    data_labels = []
    
    for year in range(int(start_year), int(end_year) + 1):
      for sem in semesters:
        try:
          val = df.loc[(df['year'] == year)
                       & (df['semester'] == sem)]['osi_count'].values[0]
        
        except:
          val = None
        try:
          label = df.loc[(df['year'] == year)
                         & (df['semester'] == sem)]['reliability'].values[0]
        except:
          label = None
        
        y.append(val)
        data_labels.append(label)
    
    trace = go.Scatter(
      x=x,
      y=y,
      name=names[j],
      line=go.scatter.Line(width=3, color=colours[j], dash='dash'),
      connectgaps=True,
      mode='lines+text',
      text=data_labels,
      showlegend=True,
      textposition='top center'
    )
    traces.append(trace)
    j += 1
  
  title = '{1}({0}) vs {1}(All)<br>Enrolments & CES Responses'.format(program_code, course_code)
  fig = go.Figure(
    data=traces,
    layout=go.Layout(
      title=dict(text=title),
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
        title=dict(text='No. of Students'),
        ticklen=5,
        zeroline=True,
        zerolinewidth=2,
      ),
      width=width,
      height=height,
      hovermode='closest',
      margin=dict(b=40, l=55, r=5, t=70),
      hidesources=True,
    )
  )
  
  return fig


def line_graph_crse_prg_current(df_prg_ces,
                                df_crse_ces,
                                df_crse_prg_ces,
                                course_code,
                                program_code,
                                year=2019,
                                semester=2,
                                width=520, height=320):

  f_df_crse_ces = df_crse_ces.loc[df_crse_ces['course_code'] == course_code]
  f_df_crse_prg_ces = df_crse_prg_ces.loc[df_crse_prg_ces['course_code'] == course_code]

  f_df_prg_ces = df_prg_ces.loc[
    (df_prg_ces['year'] == year)
    & (df_prg_ces['semester'] == semester)]
  
  f_df_crse_ces = f_df_crse_ces.loc[
    (f_df_crse_ces['year'] == year)
    & (f_df_crse_ces['semester'] == semester)]

  f_df_crse_prg_ces = f_df_crse_prg_ces.loc[
    (f_df_crse_prg_ces['year'] == year)
    & (f_df_crse_prg_ces['semester'] == semester)]

  crse_prg = '{}({})'.format(course_code, program_code)
  
  title = 'Additional CES Data for Semester {1} {0}'.format(year, semester)
  
  data = [
    [course_code, 'OSI', f_df_crse_ces.iloc[0].osi, '{} responses'.format(f_df_crse_ces.iloc[0].osi_count)],
    [course_code, 'GTS', f_df_crse_ces.iloc[0].gts, None],
    [course_code, 'GTS1', f_df_crse_ces.iloc[0].gts1, None],
    [course_code, 'GTS2', f_df_crse_ces.iloc[0].gts2, None],
    [course_code, 'GTS3', f_df_crse_ces.iloc[0].gts3, None],
    [course_code, 'GTS4', f_df_crse_ces.iloc[0].gts4, None],
    [course_code, 'GTS5', f_df_crse_ces.iloc[0].gts5, None],
    [course_code, 'GTS6', f_df_crse_ces.iloc[0].gts6, None],
    [crse_prg, 'OSI', f_df_crse_prg_ces.iloc[0].osi, '{} responses'.format(f_df_crse_prg_ces.iloc[0].osi_count)],
    [crse_prg, 'GTS', f_df_crse_prg_ces.iloc[0].gts, None],
    [crse_prg, 'GTS1', f_df_crse_prg_ces.iloc[0].gts1, None],
    [crse_prg, 'GTS2', f_df_crse_prg_ces.iloc[0].gts2, None],
    [crse_prg, 'GTS3', f_df_crse_prg_ces.iloc[0].gts3, None],
    [crse_prg, 'GTS4', f_df_crse_prg_ces.iloc[0].gts4, None],
    [crse_prg, 'GTS5', f_df_crse_prg_ces.iloc[0].gts5, None],
    [crse_prg, 'GTS6', f_df_crse_prg_ces.iloc[0].gts6, None],
    [program_code, 'OSI', f_df_prg_ces.iloc[0].osi, '{} responses'.format(f_df_prg_ces.iloc[0].osi_count)],
    [program_code, 'GTS', f_df_prg_ces.iloc[0].gts, None],
    [program_code, 'GTS1', f_df_prg_ces.iloc[0].gts1, None],
    [program_code, 'GTS2', f_df_prg_ces.iloc[0].gts2, None],
    [program_code, 'GTS3', f_df_prg_ces.iloc[0].gts3, None],
    [program_code, 'GTS4', f_df_prg_ces.iloc[0].gts4, None],
    [program_code, 'GTS5', f_df_prg_ces.iloc[0].gts5, None],
    [program_code, 'GTS6', f_df_prg_ces.iloc[0].gts6, None]
  ]
  
  df = pd.DataFrame(data, columns=['Name', 'Metric', 'value', 'responses'])
  

  fig = px.bar(df,
               x="Metric", y="value", color='Name', text='responses',
               barmode='group',
               title=title,
               color_discrete_map={course_code: rc.RMIT_DarkBlue,
                                   crse_prg: rc.RMIT_Red,
                                   program_code: rc.RMIT_Blue},
               width=width, height=height)

  fig.update_layout(
    title=title,
    showlegend=False,
    yaxis=dict(
      title='Percent Agree',
      range=[0, 105],
      ticklen=5,
      zeroline=True,
      zerolinewidth=2,
    ),
    hovermode='closest',
    margin=dict(b=40, l=55, r=5, t=50),
    hidesources=True)
  
  return fig