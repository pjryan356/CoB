## Saves excel sheets into seperate files
# Peter Ryan May 2019

import os
import xlrd
from xlutils.copy import copy
import xlwt

path = 'H:\\Data\\SIM\\'
targetdir = (path)

# Make new directory
if not os.path.exists(targetdir):
  os.makedirs(targetdir)

# Get all files in directory; can add a criteris if desired.
for root, dir, files in os.walk(path, topdown=False):
  xlsfiles = [f for f in files]

# cycle through files
for f in xlsfiles:
  wb = xlrd.open_workbook(os.path.join(root, f), on_demand=True)
  
  # cycle through sheets
  for sheet in wb.sheets():
    newwb = copy(wb) # makes a temp copy of that book
    # brute force, but strips away all other sheets apart from the sheet being looked at
    newwb._Workbook__worksheets = [ worksheet for worksheet in newwb._Workbook__worksheets if worksheet.name == sheet.name ]
    # saves each sheet as the original file name plus the sheet name
    newwb.save(targetdir + "Lecturers Feedback " + sheet.name + " 201905" + ".xls")