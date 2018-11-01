# For Peter August 2018
# PUT THE PASSWORD STRING IN

from sams_helper_functions import *
import pandas as pd
from tabulate import tabulate
import openpyxl
from sams_queries import *
from postgres_queries import (qry_create_table_course_location,
                              qry_add_comment,
                              qry_drop_table,
                              qry_delete_after_term)
import datetime as dt
import psycopg2
from sqlalchemy import (create_engine, orm)
import shutil
import getpass

def copy_rename(old_file_name, new_file_name):
  import os
  
  src_dir = os.curdir
  dst_dir = os.path.join(os.curdir, "subfolder")
  src_file = os.path.join(src_dir, old_file_name)
  shutil.copy(src_file, dst_dir)
  
  dst_file = os.path.join(dst_dir, old_file_name)
  new_dst_file_name = os.path.join(dst_dir, new_file_name)
  os.rename(dst_file, new_dst_file_name)

def get_all_bus_courses(term_year, term_category):
  qry = '''
SELECT DISTINCT
    cls.course_code,
    cls.course_name,
    cls.school_code,
    cls.term_code,
    term.term_name

FROM (
    SELECT DISTINCT
      t2.STRM AS term_code,
      t2.SUBJECT || t2.CATALOG_NBR AS course_code,
      t2.DESCR AS course_name,
      t2.acad_org AS school_code

    FROM PS_CLASS_TBL t2
    WHERE t2.acad_group = 'BUS'
    ) cls
  INNER JOIN (
    SELECT DISTINCT
      t3.STRM AS term_code,
      t3.DESCRSHORT AS term_name
    FROM PS_TERM_TBL t3
    WHERE acad_year = {0} AND term_category = {1}
    ) term ON (cls.term_code = term.term_code)
'''.format(term_year, term_category)
  return qry
  
def get_course_grade_distribution(course_code, term_code='1850', st_year=2015, semester=None):
  st_term = '{}00'.format(str(int(st_year)-2000))
  if semester == None:
    sem_txt = '(1,2)'
  else:
    sem_txt = '({})'.format(semester)
  qry = '''
SELECT
	cls.course_code,
  enrl.term_code,
  term.term_name,
  sum(enrl.nn) AS nn,
  sum(enrl.pa) AS pa,
  sum(enrl.cr) AS cr,
  sum(enrl.di) AS di,
  sum(enrl.hd) AS hd

FROM (
  SELECT
    t1.CLASS_NBR,
    t1.STRM AS term_code,
    sum(CASE WHEN t1.GRD_PTS_PER_UNIT = 0 AND t1.CRSE_GRADE_OFF IN ('NN', 'DNS', 'NH', 'SP') THEN 1 ELSE 0 END) AS nn,
    sum(CASE WHEN t1.GRD_PTS_PER_UNIT = 1 THEN 1 ELSE 0 END) AS pa,
    sum(CASE WHEN t1.GRD_PTS_PER_UNIT = 2 THEN 1 ELSE 0 END) AS cr,
    sum(CASE WHEN t1.GRD_PTS_PER_UNIT = 3 THEN 1 ELSE 0 END) AS di,
    sum(CASE WHEN t1.GRD_PTS_PER_UNIT = 4 THEN 1 ELSE 0 END) AS hd

  FROM	PS_STDNT_ENRL t1
  WHERE
      t1.strm >= '{0}'
      AND t1.strm < '{1}'
      AND t1.INCLUDE_IN_GPA = 'Y'
      AND t1.STDNT_ENRL_STATUS = 'E'
      AND t1.ENRL_STATUS_REASON='ENRL'
      AND t1.GRADING_BASIS_ENRL<>'NON'

  GROUP BY t1.CLASS_NBR, t1.STRM
  ) enrl

INNER JOIN (
  SELECT DISTINCT
    t2.CLASS_NBR,
    t2.STRM AS term_code,
    t2.SUBJECT || t2.CATALOG_NBR AS course_code
  FROM PS_CLASS_TBL t2
  WHERE t2.acad_group = 'BUS' AND t2.SUBJECT || t2.CATALOG_NBR = '{2}'
  ) cls ON (cls.CLASS_NBR = enrl.CLASS_NBR AND cls.term_code = enrl.term_code)

INNER JOIN (
  SELECT DISTINCT
    t3.STRM AS term_code,
    t3.descrshort AS term_name,
    t3.term_category,
    t3.acad_year AS term_year
  FROM PS_TERM_TBL t3
  WHERE t3.acad_year >= {3} AND t3.term_category IN {4}
  ) term ON (enrl.term_code = term.term_code)
GROUP BY cls.course_code, enrl.term_code, term.term_name
ORDER BY enrl.term_code DESC
  '''.format(st_term, term_code, course_code, st_year, sem_txt)
  return(qry)






# Get current semester information

start = dt.datetime.now()
# Get all courses
#df_courses = pd.read_sql(sql=get_all_bus_courses(current_year, current_semester), con=sams_engine)

# Iterate through courses
for j in range(1):
  # get course data from sams

  # open template
  directory = 'H:\\Projects\\CoB\\Course_Assessment_Moderation\\'
  template = 'grade_distribution_template.xlsx'
  wb = openpyxl.load_workbook(directory+template)
  sheet = wb['data']

  # Input data into sheet

  sheet.cell(row=4, column=2).value = '45'

  sheet.protection.set_password('ADG')
  # Save sheet
  filename = 'grade_distribution_check.xlsx'
  wb.save(directory+filename)

  
print('It took {} seconds'.format((dt.datetime.now()-start).seconds))