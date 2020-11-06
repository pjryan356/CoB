## Copys grade distribution files into seperate shared OneDrive folders
# Peter Ryan Jan 2020

import shutil
import os
import glob
from tabulate import tabulate

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')
from general.sams_helper_functions import *
from general.sams_queries import *

# Create connections
# create sams engine this is the connection to the oracle database
password_str = input("SAMS Password: ") ## Input password
sams_engine = return_sams_engine(password_str=password_str)


current_year = 2019
term_code_final = 1992


def get_all_sbm_bus_courses(term_year, term_code):
  qry = '''
  SELECT DISTINCT
      cls.course_code,
      cls.course_name,
      cls.school_code,
      cls.term_code,
      term.term_name,
      cls.crse_id,
      cls_melb.course_code AS course_code_melb

  FROM (
      SELECT DISTINCT
        t2.STRM AS term_code,
        t2.SUBJECT || t2.CATALOG_NBR AS course_code,
        t2.DESCR AS course_name,
        t2.acad_org AS school_code,
        t2.crse_id

      FROM PS_CLASS_TBL t2
      WHERE t2.acad_group = 'BUS' AND t2.strm={1} AND enrl_tot > 0
      ) cls
    INNER JOIN (
      SELECT DISTINCT
        t3.STRM AS term_code,
        t3.DESCRSHORT AS term_name
      FROM PS_TERM_TBL t3
      WHERE acad_year = {0}
      ) term ON (cls.term_code = term.term_code)

    LEFT OUTER JOIN (
      SELECT DISTINCT
        t4.SUBJECT || t4.CATALOG_NBR AS course_code,
        t4.crse_id

      FROM PS_CLASS_TBL t4
      WHERE t4.acad_group = 'BUS' AND t4.strm IN ('2010', '1910', '1950')
      ) cls_melb ON (cls.crse_id = cls_melb.crse_id)

  '''.format(term_year, term_code)
  return qry
  

def get_school_name(school_code):
  if school_code == '610P':
    return 'CBO'
  if school_code == '615H':
    return 'ACCT'
  if school_code == '620H':
    return 'BITL'
  if school_code == '625H':
    return 'EFM'
  if school_code == '630H':
    return 'MGT'
  if school_code == '650T':
    return 'VBE'
  if school_code == '660H':
    return 'GSBL'
  if school_code == 'VN':
    return 'Not CoB'
  return None

# Get all SIM courses
df_courses = pd.read_sql(sql=get_all_sbm_bus_courses(current_year, term_code_final), con=sams_engine)
print(tabulate(df_courses, headers='keys'))

newfolders = []

# Directory containing files
for i_course, r in df_courses.iterrows():
  school = get_school_name(r['school_code'])
  destination = 'C:\\Users\e35137\\RMIT University\\' \
                'GRP-CoBLearningandTeachingPortfolio - {0} (Shared)\\Course Folders ({0})' \
                ''.format(school)
  for (dirpath, dirnames, filenames) in os.walk(destination):
    if r['course_code_melb'] in dirnames:
      dstpath = '{0}\\{1}\\{2}\\'.format(destination, r['course_code_melb'], r['course_code'])

      print(dstpath)
      if not os.path.exists(dstpath):
        print(dstpath)
        print('\n')
        os.mkdir(dstpath)
        newfolders.append(dstpath)
      break
      
    else:
      continue

print('\n\n')
for txt in newfolders:
  print(txt)
    

