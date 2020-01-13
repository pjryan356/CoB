## Saves excel sheets into seperate files
# Peter Ryan May 2019

import os
import xlrd
from xlutils.copy import copy
import xlwt



def split_excel_into_sheets(r, f, targetdir, target_file_start, target_file_end):
  wb = xlrd.open_workbook(os.path.join(r, f), on_demand=True)
  
  # cycle through sheets
  for sheet in wb.sheets():
    newwb = copy(wb)  # makes a temp copy of that book
    # brute force, but strips away all other sheets apart from the sheet being looked at
    newwb._Workbook__worksheets = [worksheet for worksheet in newwb._Workbook__worksheets if
                                   worksheet.name == sheet.name]
    # saves each sheet as the original file name plus the sheet name
    newwb.save(targetdir + target_file_start + sheet.name + target_file_end + ".xls")


for school in ['Accountancy', 'Econ & Fin', 'Logistics', 'Management & Int Bus', 'Marketing']:
  path = 'H:\\Data\\SIM\\{0}\\2019S2\\'.format(school)

  # Make target directory
  targetdir = '{}'.format(path)
  if not os.path.exists(targetdir):
    os.makedirs(targetdir)

  for root, dir, files in os.walk(path, topdown=False):
    for file in files:
      split_excel_into_sheets(root, file, targetdir, "Lecturers Feedback ", " 2019 July")


    