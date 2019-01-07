## Creates course assessment files for CAC purposes
# Peter Ryan Nov 2018

import pandas as pd
import openpyxl
from openpyxl.styles import Alignment
import shutil
from tabulate import tabulate

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')


def copy_rename(old_file_name, new_file_name):
  import os
  
  src_dir = os.curdir
  dst_dir = os.path.join(os.curdir, "subfolder")
  src_file = os.path.join(src_dir, old_file_name)
  shutil.copy(src_file, dst_dir)
  
  dst_file = os.path.join(dst_dir, old_file_name)
  new_dst_file_name = os.path.join(dst_dir, new_file_name)
  os.rename(dst_file, new_dst_file_name)



# open template
directory = 'H:\\Projects\\CoB\\Program Transformation\\CLO mapping\\'
plo_clo_filename = 'PLOs_CLOs_manually_editted.xlsx'

template = 'PLO_CLO_alignment_template_1.xlsx'

# open template
#wb = openpyxl.load_workbook(directory+template)



# Get Dataframes
df_plo = pd.read_excel(directory+plo_clo_filename, sheetname='PLOs')
df_clo = pd.read_excel(directory+plo_clo_filename, sheetname='CLOs')
df_mapping = pd.read_excel(directory+plo_clo_filename, sheetname='Mapping')

print(tabulate(df_mapping, headers='keys'))



