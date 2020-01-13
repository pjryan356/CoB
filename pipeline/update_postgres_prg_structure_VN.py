## Update script to upload program detials table in local db
# Peter Ryan 2019 Feb

import datetime as dt
import psycopg2
from sqlalchemy import (create_engine, orm, String)
import pandas as pd
from tabulate import tabulate

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc
from general.sams_queries import *
from general.sams_helper_functions import *
from general.postgres_queries import (
  qry_delete_after_term)

# Get inputs
password_str = input("SAMS Password: ")

# Create connections
# create sams engine this is the connection to the oracle database
sams_engine = return_sams_engine(password_str=password_str)

# create postgres engine this is the connection to the oracle database
postgres_user = 'pjryan'
postgres_host = 'localhost'
postgres_dbname = 'postgres'
postgres_pw = input("Postgres Password: ")

engine_string = 'postgresql+psycopg2://{}:{}@{}/{}'.format(postgres_user,
                                                           postgres_pw,
                                                           postgres_host,
                                                           postgres_dbname)
postgres_engine = create_engine(engine_string)
postgres_con = postgres_engine.connect()


# get data from sams
sams_qry = qry_program_course_structure(program_code=None, active=False)

sams_qry = '''
SELECT
        prg.acad_prog AS program_code,
        prg.acad_plan AS plan_code,
        prg.effdt,
        prg.program_name,
        prg.acad_career AS program_level,
        prg.acad_org AS program_school_code,
        CASE
            WHEN prg.campus = 'VNMRI' THEN 'SBM'
            WHEN prg.acad_org = '610P' THEN 'CBO'
            WHEN prg.acad_org = '615H' THEN 'ACCT'
            WHEN prg.acad_org = '620H' THEN 'BITL'
            WHEN prg.acad_org = '625H' THEN 'EFM'
            WHEN prg.acad_org = '630H' THEN 'MGT'
            WHEN prg.acad_org = '650T' THEN 'VBE'
            WHEN prg.acad_org = '660H' THEN 'GSBL'
            ELSE 'UNK'
            END AS school_abbr,
        prg.acad_group AS program_college,
        prg.campus,
        prg_crse.campus AS crse_campus,
        prg_crse.crse_id,
        prg_crse.course_code,
        prg_crse.course_name,
        prg_crse.ams_block_nbr,
        clist_hdr.clist_name,
        crse_list_effdt
      FROM (
        SELECT
          t1.acad_prog,
          t1.acad_plan,
          t1.acad_career,
          t1.acad_org,
          t1.acad_group,
          t1.campus,
          t1.descr AS program_name,
          t1.effdt
        FROM PS_ACAD_PROG_TBL t1
        WHERE t1.EFF_STATUS = 'A'
          AND acad_group = 'BUS'

          AND t1.EFFDT = (
            SELECT max(EFFDT)
            FROM  PS_ACAD_PROG_TBL t2
            WHERE t2.EFF_STATUS = 'A'
              AND t2.acad_prog = t1.acad_prog
              AND t2.acad_career = t1.acad_career
              AND t2.campus = t1.campus
              AND t1.campus != ' ')
          AND t1.campus != ' '
        ) prg

      LEFT OUTER JOIN (
        SELECT
          acad_prog,
          acad_plan,
          crse_career,
          campus,
          course_list,
          descr1 AS plan_name,
          descr254 AS explaination,
          ams_block_nbr,
          r_course_sequence,
          descr254A AS explaination2,
          ams_descr254A AS explaination3,
          crse_id,
          SUBJECT || catalog_nbr AS course_code,
          ams_descr254 AS course_name
        FROM PS_AMS_SIM_PRG_STR
        ) prg_crse ON (prg.acad_prog = prg_crse.acad_prog AND prg.acad_plan = prg_crse.acad_plan AND prg.acad_career=prg_crse.crse_career)

      LEFT OUTER JOIN (
        SELECT DISTINCT course_list, descr254A AS clist_name, descr AS clist_namelong, descrshort AS clist_nameshort, acad_prog, acad_plan, acad_career, effdt AS crse_list_effdt
        FROM PS_CLST_MAIN_TBL t2
        WHERE t2.EFF_STATUS = 'A'
          AND t2.EFFDT = (SELECT max(EFFDT) FROM PS_CLST_MAIN_TBL maxdt WHERE maxdt.course_list = t2.course_list AND maxdt.acad_prog = t2.acad_prog AND maxdt.EFF_STATUS = 'A' AND maxdt.acad_plan = t2.acad_plan AND maxdt.acad_career = t2.acad_career)
        ) clist_hdr ON (clist_hdr.acad_prog=prg.acad_prog AND clist_hdr.acad_plan = prg.acad_plan AND clist_hdr.acad_career = prg.acad_career AND clist_hdr.course_list = prg_crse.course_list )
      WHERE prg_crse.campus LIKE '%VN%'
      ORDER BY prg.acad_prog, prg_crse.campus, ams_block_nbr, r_course_sequence, course_code
'''
try:
  df = pd.read_sql(sql=sams_qry, con=sams_engine)
except:
  print(sams_qry)

df.to_csv('H:\\file.csv')
print(tabulate(df, headers='keys'))

int('df')

df.to_sql(name='tbl_plan_course_structure',
          con=postgres_engine,
          schema='programs',
          if_exists='append',
          index=False,
          dtype={"program_code": String(), "plan_code": String()}
          )

# Add update statement to table description
date = dt.datetime.now().date()
qry_comment = """
COMMENT ON TABLE {1}.{2}
    IS 'Updated on {0}'
;
""".format(date.strftime('%d-%m-%Y'), 'programs', 'tbl_plan_course_structure')

print(qry_comment)
trans = postgres_con.begin()
postgres_con.execute(qry_comment)
trans.commit()



