## Copys Course Data Packs into speerate course folders

# Peter Ryan 2019 Nov

import shutil
import os
import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')


def create_directory(dirName):
  import os
  if not os.path.exists(dirName):
    os.mkdir(dirName)
    print("Directory ", dirName, " Created ")
  else:
    print("Directory ", dirName, " already exists")
    
# Create connections
# create sams engine this is the connection to the oracle database

semester = '2020S1'
semester = input("Input Semester [e.g. 2019S1]: ") ## Input password

folder = 'H:\\Projects\\CoB\\Surveys\\CES\\Course Enhancement\\2020 S1\\DataPacks\\'

for sch in ['ACCT', 'BITL', 'EFM', 'GSBL', 'MGT', 'VBE']:
  
  sch_folder = folder + '{}\\'.format(sch)
  
  print(sch_folder)
  for filename in os.listdir(sch_folder):
    if filename.endswith(".pdf"):
      course_code = filename.split(' ')[0]
      crse_folder = sch_folder+'{}\\'.format(course_code)
      #create_directory(crse_folder)

      #shutil.copy(sch_folder+filename, crse_folder+filename)
      print(crse_folder+filename)
      continue
    else:
      continue