import plotly
from tabulate import tabulate
import plotly.graph_objs as go
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


def sim_line_graph_measure_surveys(df1,
                                   course_code,
                                   measures=['subject_content', 'lecturer_effectiveness', 'course_satisfaction'],
                                   start_year=2017,
                                   end_year=2019, semester=None,
                                   width=520, height=300):
  f_df = df1.loc[df1['course_code'] == course_code]
  
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
  
  graph_title = ''
  
  for measure in measures:
    graph_title += '{}, '.format(get_name(measure))
    for staff_type in ['Local', 'RMIT']:
      data_label = []
      y = []
      label_check += 1
      for year in range(int(start_year), int(end_year) + 1):
        for sem in semesters:
          try:
            val = pd.to_numeric(f_df.loc[(f_df['year'] == int(year)) & (f_df['semester'] == int(sem)) & (
                f_df['staff_type'] == staff_type)].iloc[0][measure])
          except:
            val = None
          y.append(val)
      
      trace = go.Scatter(
        x=x,
        y=y,
        name='{}'.format(staff_type),
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
        connectgaps=False,
        mode='lines+markers',
        showlegend=True,
        textposition='top center'
      )
      traces.append(trace)
  
  graph_title = graph_title[:-2] + ' '
  
  title = 'SIM {} {}'.format(graph_title[:-1], course_code)
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
        range=[3.45, 4.55],
        tickvals=[3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5],
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
  return fig

def sim_line_graph_measure_surveys_mulitiple(df1,
                                   course_code,
                                   measures=['subject_content', 'lecturer_effectiveness', 'course_satisfaction'],
                                   start_year=2017,
                                   end_year=2019, semester=None,
                                   width=520, height=320):
  f_df = df1.loc[df1['course_code'] == course_code]

  # all traces for plotly
  traces = []
  
  xlabels = []
  
  for year in range(int(start_year), int(end_year)+1):
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
  
  graph_title = ''
  
  for measure in measures:
    for staff_type in ['Local', 'RMIT']:
      data_label = []
      y = []
      label_check += 1
      for year in range(int(start_year), int(end_year) + 1):
        for sem in semesters:
          try:
            val = pd.to_numeric(f_df.loc[(f_df['year'] == int(year)) & (f_df['semester'] == int(sem)) & (f_df['staff_type'] == staff_type)].iloc[0][measure])
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
        connectgaps=False,
        mode='lines+markers',
        showlegend=True,
        textposition='top center'
      )
      traces.append(trace)

  graph_title = graph_title[:-2] + ' '
  
  title = '{} Data for {}'.format(graph_title[:-1], course_code)
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
             range=[0.5, 5.5],
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
  return fig


def graphCourseProgramPie(df1, category):
  '''
  Produce a pie chart of program population in a course
  :param df_prg: dataframe containing course measures by program
  :return: pier chart of course program proportions
  '''
  
  if category == 'college':
    df1 = df1.groupby(['college',
                       'college_name',
                       'college_name_short',
                       'college_colour'],
                      as_index=False).agg({'population': sum})
    total = int(df1['population'].sum())
    title = 'By College'
    
    traces = [go.Pie(
      labels=df1['college_name_short'],
      values=df1['population'],
      marker=dict(colors=df1['college_colour']),
      hovertext=df1['college_name'],
      hoverinfo='hovertext',
      direction="clockwise",
      rotation=0,
      hole=.3,
      opacity=1,
      showlegend=True,
      textinfo='none'
    )]
  
  if category == 'school':
    df1 = df1.groupby(['school_code',
                       'school_name',
                       'school_name_short',
                       'school_colour'],
                      as_index=False).agg({'population': sum})
    total = df1['population'].sum()
    title = 'By School'
    traces = [go.Pie(
      labels=df1['school_name_short'],
      values=df1['population'],
      marker=dict(colors=df1['school_colour']),
      hovertext=df1['school_name'],
      hoverinfo='hovertext',
      direction="clockwise",
      rotation=0,
      hole=.3,
      opacity=1,
      showlegend=True,
      textinfo='none'
    )]

  colours = [rc.RMIT_DarkBlue,
             rc.RMIT_Green,
             rc.RMIT_Red,
             rc.RMIT_Blue,
             rc.RMIT_Lavender,
             rc.RMIT_Orange]
  
  if category == 'program':
    df1.sort_values('population')
    total = df1['population'].sum()
    prg_count = len(df1)
    title = 'By Program'
    # Limit to 5 program_entries
    df1_large = df1.nlargest(5, 'population')

    # create None dataframe
    other_total = total - df1_large['population'].sum()
    other_prg_count = prg_count - len(df1_large)
    d_other = {'term_code': 'NA',
               'course_code': 'NA',
               'program_code': 'Other ({})'.format(other_prg_count),
               'population': other_total,
               'program_name': 'Other ({} programs)'.format(other_prg_count),
               'school_code': 'NA',
               'school_name': 'NA',
               'school_name_short': 'NA',
               'school_colour': 'NA',
               'college': 'NA',
               'college_name': 'NA',
               'college_name_short': 'NA',
               'college_colour': 'NA'}

    df1_large = df1_large.append(d_other, ignore_index=True)
    traces = [go.Pie(
      labels=df1_large['program_code'],
      values=df1_large['population'],
      hovertext=df1_large['program_name'],
      hoverinfo='hovertext',
      marker=dict(colors=colours),
      hole=.3,
      direction="clockwise",
      rotation=0,
      opacity=1,
      showlegend=True,
      textinfo='none'
    )]

  layout = go.Layout(
    title=title,
    showlegend=True,
    width=335,
    height=250,
    margin=dict(b=10, l=10, r=100, t=35),
    annotations=[
      {'font': {'size': 16},
       'text': '{}<br>ppl'.format(total),
       'x': 0.5,
       'y': 0.5,
       'showarrow': False}
    ]
  )
  
  fig = {'data': traces,
         'layout': layout}
  
  return fig

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def generate_sim_ces_table(df1, course_code):
  f_df = df1.loc[df1['course_code'] == course_code]
  
  table = html.Table(
    # Header
    [
      html.Tr(
        [html.Th('Year', style={'text-align': 'center'}),
         html.Th('Sem'),
         html.Th('Pop'),
         html.Th('Res'),
         html.Th('Staff'),
         html.Th('Content'),
         html.Th('Lecturer'),
         html.Th('Satisfaction'),
         ],
        style={'border': 'solid',
               'max_height': 5 }
      )
    ] +
    
    # Body
    [
      html.Tr(
        [html.Td(f_df.iloc[i][col]) for col in ('year',
                                                'semester',
                                                'population',
                                                'responses',
                                                'staff_type',
                                                'subject_content',
                                                'lecturer_effectiveness',
                                                'course_satisfaction')],
        style={'width': 1,
               'height': 5}
      ) for i in range(len(f_df))],
    style={'border': 'solid',
           'font-size': 11,
           'wdith': 400,
           'height': 5,
           'alignment': 'centre'},
  )
  return table


def generate_sim_ces_pd_table(df1, course_code):
  f_df = df1.loc[df1['course_code'] == course_code]
  
  h = ['<br>Year<br>', '<br>S<br>', '<br>Staff<br>',
       '<br>Pop<br>', '<br>Res<br>',
       '<br>S Con<br>', '<br>L Eff<br>', '<br>C Sat<br>']
  trace = go.Table(
    type='table',
    columnorder=(1, 2, 3, 4, 5, 6, 7, 8),
    columnwidth=[18, 8, 18, 16, 16, 18, 18, 18],
    header=dict(line=dict(color=rc.RMIT_White),
                values=h,
                font=dict(size=18,
                          color=rc.RMIT_White),
                height=40,
                format=dict(border='solid'),
                fill=dict(color=rc.RMIT_DarkBlue)
                ),
    cells=dict(line=dict(color=[rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_White, rc.RMIT_White]),
               values=[f_df.year, f_df.semester, f_df.staff_type,
                       f_df.population, f_df.responses,
                       f_df.subject_content, f_df.lecturer_effectiveness, f_df.course_satisfaction],
               font=dict(size=12,
                         color=[rc.RMIT_White, rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_Black, rc.RMIT_Black,
                                rc.RMIT_Black, rc.RMIT_Black, rc.RMIT_Black
                                ]),
               height=28,
               format=dict(border='solid'),
               fill=dict(
                 color=[rc.RMIT_DarkBlue, rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                        rc.RMIT_Arctic, rc.RMIT_Arctic,
                        rc.RMIT_Azure, rc.RMIT_Azure, rc.RMIT_Azure]),
               ),
  )
  
  layout = go.Layout(width=574,
                     height=324,
                     margin=dict(b=10, l=10, r=10, t=10))
  data = [trace]
  fig = dict(data=data, layout=layout)
  return fig


def graphCourseProgramPie(df1, category):
  '''
  Produce a pie chart of program population in a course
  :param df_prg: dataframe containing course measures by program
  :return: pier chart of course program proportions
  '''
  
  if category == 'college':
    df1 = df1.groupby(['college',
                       'college_name_short',
                       'college_colour'],
                      as_index=False).agg({'population': sum})
    total = df1['population'].sum()
    title = 'By College'
    
    traces = [go.Pie(
      labels=df1['college_name_short'],
      values=df1['population'],
      marker=dict(colors=df1['college_colour']),
      direction="clockwise",
      rotation=0,
      hole=.3,
      opacity=1,
      showlegend=True,
      textinfo='none'
    )]
  
  if category == 'school':
    df1 = df1.groupby(['school_code',
                       'school_name_short',
                       'school_colour'],
                      as_index=False).agg({'population': sum})
    total = df1['population'].sum()
    title = 'By School'
    traces = [go.Pie(
      labels=df1['school_name_short'],
      values=df1['population'],
      marker=dict(colors=df1['school_colour']),
      direction="clockwise",
      rotation=0,
      hole=.3,
      opacity=1,
      showlegend=True,
      textinfo='none'
    )]
  
  colours = [rc.RMIT_DarkBlue,
             rc.RMIT_Green,
             rc.RMIT_Red,
             rc.RMIT_Blue,
             rc.RMIT_Lavender,
             rc.RMIT_Orange]
  
  if category == 'program':
    df1.sort_values('population')
    total = df1['population'].sum()
    prg_count = len(df1)
    title = 'By Program'
    # Limit to 5 program_entries
    df1_large = df1.nlargest(5, 'population')
    
    # create None dataframe
    other_total = total - df1_large['population'].sum()
    other_prg_count = prg_count - len(df1_large)
    d_other = {'term_code': 'NA',
               'course_code': 'NA',
               'program_code': 'Other ({})'.format(other_prg_count),
               'population': other_total,
               'program_name': 'Other ({} programs)'.format(other_prg_count),
               'school_code': 'NA',
               'school_name_short': 'NA',
               'school_colour': 'NA',
               'college': 'NA',
               'college_name_short': 'NA',
               'college_colour': 'NA'}
    
    df1_large = df1_large.append(d_other, ignore_index=True)
    traces = [go.Pie(
      labels=df1_large['program_code'],
      values=df1_large['population'],
      hovertext=df1_large['program_name'],
      hoverinfo='hovertext',
      marker=dict(colors=colours),
      hole=.3,
      direction="clockwise",
      rotation=0,
      opacity=1,
      showlegend=True,
      textinfo='none'
    )]
  
  layout = go.Layout(
    title=title,
    showlegend=True,
    width=335,
    height=250,
    margin=dict(b=10, l=10, r=100, t=35),
    annotations=[
      {'font': {'size': 16},
       'text': '{}<br>ppl'.format(total),
       'x': 0.5,
       'y': 0.5,
       'showarrow': False}
    ]
  )
  
  fig = {'data': traces,
         'layout': layout}
  
  return fig





