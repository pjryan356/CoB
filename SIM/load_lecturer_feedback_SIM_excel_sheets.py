## Saves excel sheets into seperate files
# Peter Ryan May 2019

import os
import xlrd
from xlutils.copy import copy
import xlwt






for school in ['Accountancy', 'Econ & Fin', 'Logistics', 'Management & Int Bus', 'Marketing']:
  path = 'H:\\Data\\SIM\\{0}\\2019S2\\'.format(school)

  # Make target directory
  targetdir = '{}'.format(path)
  if not os.path.exists(targetdir):
    os.makedirs(targetdir)

  for root, dir, files in os.walk(path, topdown=False):
    for file in files:
      load_excel_to_db(root, file, "Lecturers Feedback ", " 2019 July")


def load_excel_to_db(r, f, targetdir, target_file_start):
  wb = xlrd.open_workbook(os.path.join(r, f), on_demand=True)
  
  # cycle through sheets
  for sheet in wb.sheets():
    newwb = copy(wb)  # makes a temp copy of that book
    # brute force, but strips away all other sheets apart from the sheet being looked at
    newwb._Workbook__worksheets = [worksheet for worksheet in newwb._Workbook__worksheets if
                                   worksheet.name == sheet.name]
    # saves each sheet as the original file name plus the sheet name
    newwb.save(targetdir + target_file_start + sheet.name + target_file_end + ".xls")


df = pd.read_excel(directory + filename,
                   sheet_name='RMIT Lec',
                   skiprows=1,
                   usecols=[6, 7, 8, 9, 11, 16, 17, 18, 19, 20, 21, 22],
                   skipfooter=0)

df.columns = ['subject', 'catalog', 'course_name', 'section_code', 'teaching_staff',
              'responses', 'population',
              'subject_content', 'lecturer_effectiveness', 'course_satisfaction',
              'comment_type', 'comment_text'
              ]