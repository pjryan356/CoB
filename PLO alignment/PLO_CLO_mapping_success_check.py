## Creates course assessment files for CAC purposes
# Peter Ryan Nov 2018

import pandas as pd
import openpyxl
from openpyxl.styles import Protection
from openpyxl.styles import Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from tabulate import tabulate


import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')



# open template
directory = 'H:\\Projects\\CoB\\Program Transformation\\CLO mapping\\Success\\'
plo_clo_filename = 'PLOs_CLOs_manually_editted_success.xlsx'

template = 'PLO_CLO_alignment_template_success.xlsx'

# Get Dataframes
df_plo = pd.read_excel(directory+plo_clo_filename, sheet_name='PLOs')
df_clo = pd.read_excel(directory+plo_clo_filename, sheet_name='CLOs', converters={'course_id': str})
df_mapping = pd.read_excel(directory+plo_clo_filename, sheet_name='Mapping', converters={'course_id': str})

# get program list
df_programs = df_mapping[['program_code', 'plan_code', 'career', 'school_code',
                          'school_abbr', 'campus', 'program_name']].drop_duplicates()


bad_clo_list = []
# iterate through programs
for i_prg, prg in df_programs.iterrows():
  # open template
  wb = openpyxl.load_workbook(directory + template)

  # Update PLO sheet
  # Open PLO sheet
  ws = wb["PLOs"]
  
  df_prg_plos = df_plo.loc[(df_plo['program_code'] == prg['program_code']) & (df_plo['plan_code'] == prg['plan_code'])]
  
  if len(df_prg_plos) <= 2:
    print(prg['program_code'], prg['plan_code'], len(df_prg_plos))
  
  # Update mapping sheet
  # Open Mapping sheet
  ws = wb["Program_course_mapping"]

  df_prg_mapping = df_mapping.loc[(df_mapping['program_code'] == prg['program_code']) & (df_mapping['plan_code'] == prg['plan_code'])]
  
  for i, r in df_prg_mapping.iterrows():
    df_prg_crse_clos = df_clo.loc[(df_clo['course_id'] == r['course_id'])]
    if len(df_prg_crse_clos) <= 2:
      bad_clo_list.append([r['course_id'], r['course_code'], len(df_prg_crse_clos)])

print('\n')
for crse in bad_clo_list:
  print(crse)



