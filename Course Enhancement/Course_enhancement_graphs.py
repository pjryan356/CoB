import plotly
from tabulate import tabulate
import plotly.graph_objs as go
import pandas as pd
import traceback
import dash_html_components as html

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc
from Course_enhancement_functions import get_colour

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
              
def line_graph_measure_surveys(df1,
                               course_code,
                               measures=['gts', 'osi'],
                               start_year=2014,
                               end_year=2018, semester=None,
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
  target = [75 for i in range(1, no_terms + 1)]
  
  label_check = 0
  
  graph_title = ''
  
  for measure in measures:
    graph_title += '{}, '.format(measure.upper())
    data_label = []
    y = []
    label_check += 1
    for year in range(int(start_year), int(end_year) + 1):
      for sem in semesters:
        try:
          val = pd.to_numeric(f_df.loc[(f_df['survey_year'] == str(year)) & (f_df['survey_semester'] == int(sem))].iloc[0][measure])
        except:
          val = None
        y.append(val)
        
        # Only put data_labels on first trace
        if label_check == 1:
          try:
            val = f_df.loc[(f_df['survey_year'] == str(year)) & (f_df['survey_semester'] == int(sem))].iloc[0]['reliability']
          except:
            val = None
          data_label.append(str(val))
    
    trace = go.Scatter(
      x=x,
      y=y,
      name=measure.upper(),
      text=data_label,
      line=go.Line(width=2, color=get_colour(measure)),
      marker=go.Marker(
        color=get_colour(measure),
        size=8,
        symbol='diamond'
      ),
      connectgaps=False,
      mode='lines+markers+text',
      showlegend=True,
      textposition='top center'
    )
    traces.append(trace)

  graph_title = graph_title[:-2] + ' '

  trace_target = go.Scatter(
    x=x,
    y=target,
    line=go.Line(width=2, color=rc.RMIT_Red),
    connectgaps=False,
    mode='lines',
    showlegend=False)
  
  #traces.append(trace_target)
  
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
             title='Percent Agree',
             range=[-1, 101],
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

  # plotly.offline.plot(fig, filename='C:\\Peter\\CoB\\CES Response Rates\\course_enhancement_{}.html'.format(course_code))
  # plotly.offline.plot(fig, filename='C:\\Peter\\CoB\\CES Response Rates\\course_enhancement_{}_{}.html'.format(course_code, measure))
  return fig


def line_graph_program_measure_surveys(df1,
                                       course_code,
                                       measure='gts',
                                       start_year=2014,
                                       end_year=2018, semester=None,
                                       width=520, height=320):
  # get top 5 programs in most recent semester
  f_df = df1.loc[df1['course_code'] == course_code]
  f_df1 = f_df.loc[(f_df['year'] == end_year) & (f_df['semester'] == 1)]
  program_codes = f_df1.sort_values('population', ascending=False).head(n=5)['program_code'].tolist()
  
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
             rc.RMIT_Green,
             rc.RMIT_Red,
             rc.RMIT_Lavender,
             rc.RMIT_Blue]
  
  for program_code in program_codes:
    
    data_label = []
    y = []
    label_check += 1
    for year in range(int(start_year), int(end_year) + 1):
      for sem in semesters:
        try:
          val = pd.to_numeric(
            f_df.loc[(f_df['year'] == year)
                     & (f_df['semester'] == sem)
                     & (f_df['program_code'] == program_code)].iloc[0][measure])
        except:
          val = None
        y.append(val)
    ### Editted up to here
    trace = go.Scatter(
      x=x,
      y=y,
      name=program_code,
      line=go.Line(width=2, color=colours[j]),
      marker=go.Marker(
        color=colours[j],
        size=8,
        symbol='diamond'
      ),
      connectgaps=False,
      mode='lines+markers',
      showlegend=True,
      textposition='top center'
    )
    traces.append(trace)
    j += 1

  title = '{} Data by program'.format(measure.upper())
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
        title='Percent Agree',
        range=[-1, 101],
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

def line_graph_gtsq_surveys(df1,
                            course_code,
                            start_year, end_year,
                            semester=None, acad_career='HE',
                            width=520, height=320):
  f_df = df1.loc[df1['course_code'] == course_code]
  if acad_career == None:
    acad_career = f_df['level'].tolist()[-1]
    
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
  
  for i in range(1, 7):
    measure = 'gts{}'.format(i)
    y = []

    for year in range(int(start_year), int(end_year) + 1):
      for sem in semesters:
        try:
          val = pd.to_numeric(f_df.loc[(f_df['survey_year'] == str(year)) & (f_df['survey_semester'] == int(sem))].iloc[0][measure])
        except:
          val = None
        y.append(val)
        
    xi = [k-0.175+i/20.0 for k in x]
    trace = go.Scatter(
      x=xi,
      y=y,
      name=measure.upper(),
      line=go.Line(width=2, color=get_colour(measure, level=acad_career)),
      marker=go.Marker(
        color=get_colour(measure, level=acad_career),
        size=5,
        symbol='diamond'
      ),
      connectgaps=False,
      mode='lines+markers',
      showlegend=True,
      textposition='top center'
    )
  
    traces.append(trace)
  
  title = '{} for {}'.format('Individual GTS items', course_code)
  
  fig = {'data': traces,
         'layout': go.Layout(
           title=title,
           showlegend=True,
           xaxis=dict(
             range=[0, no_terms],
             tickvals=x,
             ticktext=xlabels,
             ticks='outside',
             showgrid=False,
             tick0=1,
             dtick=1,
             ticklen=5,
             zeroline=True,
             zerolinewidth=2,
           ),
           yaxis=dict(
             title='Percent Agree',
             range=[-1, 101],
             ticklen=5,
             zeroline=True,
             zerolinewidth=2,
           ),
           width=width,
           height=height,
           hovermode='closest',
           margin=dict(b=40, l=50, r=0, t=50),
           hidesources=True,
         )
         }
  # plotly.offline.plot(fig, filename='C:\\Peter\\CoB\\CES Response Rates\\course_enhancement_{}_{}.html'.format(course_code, measure))
  # plotly.offline.plot(fig, filename='C:\\Peter\\CoB\\CES Response Rates\\course_enhancement_{}_{}.html'.format(course_code, measure))
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
    total = df1['population'].sum()
    title = 'By College'
    
    traces = [go.Pie(
      labels=df1['college_name_short'],
      values=df1['population'],
      marker=dict(colors=df1['college_colour']),
      hovertext=df1['college_name'],
      hoverinfo='hovertext',
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
      hole=.3,
      opacity=1,
      showlegend=True,
      textinfo='none'
    )]
  
  if category == 'program':
    df1.sort_values('population')
    total = df1['population'].sum()
    prg_count = len(df1)
    title = 'By Program'
    # Limit to 9 program_entries
    df1_large = df1.nlargest(9, 'population')

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
        hole=.3,
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

def generate_ces_table(df1, course_code):
  f_df = df1.loc[df1['course_code'] == course_code]
  
  table = html.Table(
    # Header
    [
      html.Tr(
        [html.Th('Year', style={'text-align': 'center'}),
         html.Th('Sem'),
         html.Th('Pop'),
         html.Th('Rel'),
         html.Th('OSI'),
         html.Th('GTS'),
         html.Th('GTS1'),
         html.Th('GTS2'),
         html.Th('GTS3'),
         html.Th('GTS4'),
         html.Th('GTS5'),
         html.Th('GTS6'),
         ],
        style={'border': 'solid',
               'max_height': 5 }
      )
    ] +
    
    # Body
    [
      html.Tr(
        [html.Td(f_df.iloc[i][col]) for col in ('survey_year',
                                                'survey_semester',
                                                'survey_population',
                                                'reliability',
                                                'osi',
                                                'gts',
                                                'gts1',
                                                'gts2',
                                                'gts3',
                                                'gts4',
                                                'gts5',
                                                'gts6')],
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


def generate_ces_pd_table(df1, course_code):
  f_df = df1.loc[df1['course_code'] == course_code]
  
  h = ['<br>Year<br>', '<br>S<br>', '<br>Pop<br>', '<br>Rel<br>',
       '<br>OSI<br>', '<br>GTS<br>', '<br>Q1<br>', '<br>Q2<br>',
       '<br>Q3<br>', '<br>Q4<br>', '<br>Q5<br>', '<br>Q6<br>']
  trace = go.Table(
    type='table',
    columnorder=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
    columnwidth=[20, 10, 20, 15, 20, 20, 20, 20, 20, 20, 20, 20],
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
                                rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_White, rc.RMIT_White]),
               values=[f_df.survey_year, f_df.survey_semester, f_df.survey_population, f_df.reliability,
                       f_df.osi, f_df.gts, f_df.gts1, f_df.gts2, f_df.gts3, f_df.gts4, f_df.gts5, f_df.gts6],
               font=dict(size=12,
                         color=[rc.RMIT_White, rc.RMIT_White,
                                rc.RMIT_Black, rc.RMIT_Black,
                                rc.RMIT_Black, rc.RMIT_Black,
                                rc.RMIT_Black, rc.RMIT_Black,
                                rc.RMIT_Black, rc.RMIT_Black,
                                rc.RMIT_Black, rc.RMIT_Black]),
               height=28,
               format=dict(border='solid'),
               fill=dict(
                 color=[rc.RMIT_DarkBlue, rc.RMIT_DarkBlue,
                        rc.RMIT_Arctic, rc.RMIT_Arctic,
                        rc.RMIT_Azure, rc.RMIT_Azure,
                        rc.RMIT_Arctic, rc.RMIT_Arctic,
                        rc.RMIT_Azure, rc.RMIT_Azure,
                        rc.RMIT_Arctic, rc.RMIT_Arctic]),
               ),
  )
  
  layout = go.Layout(width=574,
                     height=324,
                     margin=dict(b=10, l=10, r=10, t=10))
  data = [trace]
  fig = dict(data=data, layout=layout)
  return fig








