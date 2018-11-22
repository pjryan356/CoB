import RMIT_colours as rc
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

#py.sign_in('pjryan356', 'l128qIdIUnxqYnhd5NmV') # Replace the username, and API key with your credentials.

import sys
sys.path.append('C:\\Peter\\CoB\\CES Response Rates\\python')

from tabulate import tabulate

import pandas as pd
import decimal
import psycopg2
import traceback

from IPython.display import display, HTML
from xhtml2pdf import pisa
import base64

from Microsurgeryies_CES import *

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

def report_block_template(report_type, graph_url, caption=''):
  if report_type == 'interactive':
    graph_block = '<iframe style="border: none;" src="{graph_url}.embed" width="100%" height="600px"></iframe>'
  elif report_type == 'static':
    graph_block = (''
                   '<a href="{graph_url}" target="_blank">'  # Open the interactive graph when you click on the image
                   '<img style="height: 400px;" src="{graph_url}.png">'
                   '</a>')

  report_block = ('' +
                  graph_block +
                  '{caption}' +  # Optional caption to include below the graph
                  '<br>' +  # Line break
                  '<a href="{graph_url}" style="color: rgb(190,190,190); text-decoration: none; font-weight: 200;" target="_blank">' +
                  'Click to comment and see the interactive graph' +  # Direct readers to Plotly for commenting, interactive graph
                  '</a>' +
                  '<br>' +
                  '<hr>')  # horizontal line

  return report_block.format(graph_url=graph_url, caption=caption)

# Utility function
def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
            source_html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

    # return True on success and False on errors
    return pisa_status.err

qry = qry_ces_metrics(level='Course',
                      schema='ces',
                      basis='course',
                      term_codes="('1410', '1450', '1510', '1550', '1610', '1650', '1710', '1750')")

df_courses = db_extract_query_to_dataframe(qry, cur, print_messages=False)

print(tabulate(df_courses.loc[df_courses['course_code'] == 'BAFI1065'], headers='keys'))
print('\n\n')
courseList = ['BUSM4370']
for course in courseList:
  fig_osi, traces_osi = graphtermline(df_courses, course, 'osi')
  fig_gts, traces_gts = graphtermline(df_courses, course, 'gts')
  
  '''
  fig = plotly.tools.make_subplots(rows=1, cols=2)
  
  for trace in traces_osi:
    fig.append_trace(trace, 1, 1)
  for trace in traces_gts:
    fig.append_trace(trace, 1, 2)
  
  fig['layout'].update(height=600, width=600, title='CES Improvement<br>'
                                                    'Course Enhancement Data: {}<br>'
                                                    '<br>'
                                                    'GTS, OSI and Individual GTS item performance overtime<br>')
  plotly.offline.plot(fig, filename='simple-subplot')
  '''
def report_block_template(report_type, graph_url, caption=''):
  if report_type == 'interactive':
    graph_block = '<iframe style="border: none;" src="{graph_url}.embed" width="100%" height="600px"></iframe>'
  elif report_type == 'static':
    graph_block = (''
                   '<a href="{graph_url}" target="_blank">'  # Open the interactive graph when you click on the image
                   '<img style="height: 400px;" src="{graph_url}.png">'
                   '</a>')

  report_block = ('' +
                  graph_block +
                  '{caption}' +  # Optional caption to include below the graph
                  '<br>' +  # Line break
                  '<a href="{graph_url}" style="color: rgb(190,190,190); text-decoration: none; font-weight: 200;" target="_blank">' +
                  'Click to comment and see the interactive graph' +  # Direct readers to Plotly for commenting, interactive graph
                  '</a>' +
                  '<br>' +
                  '<hr>')  # horizontal line

  return report_block.format(graph_url=graph_url, caption=caption)

# Utility function
def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
            source_html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

    # return True on success and False on errors
    return pisa_status.err


width = 600
height = 600

template = (''
    '<img style="width: {width}; height: {height}" src="data:image/png;base64,{image}">'
    '{caption}'                              # Optional caption to include below the graph
    '<br>'
    '<hr>'
'')

# A collection of Plotly graphs
print(fig_osi)
figures = [
    fig_osi,
    fig_gts
]

# Generate their images using `py.image.get`
images = [base64.b64encode(py.image.get(figure, width=width, height=height)).decode('utf-8') for figure in figures]

report_html = ''
for image in images:
    _ = template
    _ = _.format(image=image, caption='', width=width, height=height)
    report_html += _

display(HTML(report_html))
convert_html_to_pdf(report_html, 'C:\\Peter\\CoB\\CES Response Rates\\PDF\\report-2.pdf')