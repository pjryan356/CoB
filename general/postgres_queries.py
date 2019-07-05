## Various queries for the CoB postgres database
# Peter Ryan Feb 2019

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

from general.db_helper_functions import (
  convert_list_string_for_sql
)

def qry_drop_table(schema, table):
  qry = 'DROP TABLE {}.{};'.format(schema, table)
  return qry

def qry_create_table_course_location(schema='ms', table='course_locations'):
  qry = '''
CREATE TABLE {0}.{1}
(
    year smallint,
    semester smallint,
    level character varying(3) COLLATE pg_catalog."default",
    course_id character varying(6) COLLATE pg_catalog."default",
    course_code_ms character varying(9) COLLATE pg_catalog."default",
    campus_ms character varying(5) COLLATE pg_catalog."default",
    cc_city character varying(9) COLLATE pg_catalog."default",
    cc_brunswick character varying(9) COLLATE pg_catalog."default",
    cc_bundoora character varying(9) COLLATE pg_catalog."default",
    cc_aus_online character varying(9) COLLATE pg_catalog."default",
    cc_singapore_im character varying(9) COLLATE pg_catalog."default",
    cc_singapore_kp character varying(9) COLLATE pg_catalog."default",
    cc_china_shanghai character varying(9) COLLATE pg_catalog."default",
    cc_china_beijing character varying(9) COLLATE pg_catalog."default",
    cc_hk_ac character varying(9) COLLATE pg_catalog."default",
    cc_hk_vt character varying(9) COLLATE pg_catalog."default",
    cc_ausvn character varying(9) COLLATE pg_catalog."default",
    cc_vtn_ri character varying(9) COLLATE pg_catalog."default",
    cc_vtn_pa character varying(9) COLLATE pg_catalog."default",
    cc_vtn_rh character varying(9) COLLATE pg_catalog."default",
    cc_uph character varying(9) COLLATE pg_catalog."default",
    cc_www_ou character varying(9) COLLATE pg_catalog."default",
    cc_www_kp character varying(9) COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
  '''.format(schema, table)
  return qry

def qry_add_comment(schema, table, comment):
  qry = " COMMENT ON TABLE {0}.{1} \n" \
        " IS '{2}';".format(schema, table, comment)
  return qry

def qry_delete_after_term(schema, table, term_code='9000'):
  qry = " DELETE FROM {}.{}".format(schema, table)
  if term_code != None:
    qry += " WHERE term_code > '{}'" \
           "".format(term_code)
  return qry


def qry_course_enhancement_list(year, semester, tbl='vw100_courses', schema='course_enhancement'):
  # Returns a dataframe of the courses undergoing enhancement course in year, semester from db (cur)
  qry = " SELECT DISTINCT \n" \
        "   ce.level, ce.school_code, ce.course_code, \n" \
        "   ce.course_code_ces, \n" \
        "   ce.cluster_code, \n" \
        "   cd.school_name, cd.course_name \n" \
        " FROM ( \n" \
        "   SELECT level, school_code, course_code, course_code_ces, cluster_code  \n" \
        "	  FROM {0}.{1} \n" \
        "   WHERE year = {2} AND semester = {3} \n" \
        "       AND cob_selected IS NOT False \n" \
        "   ) ce \n" \
        " LEFT OUTER JOIN ( \n" \
        "   SELECT * FROM lookups.vw_course_details_recent \n" \
        "   ) cd ON (SPLIT_PART(cd.course_code,'-', 1) = SPLIT_PART(ce.course_code,'-', 1))\n" \
        " ORDER BY ce.school_code, ce.course_code \n" \
        "".format(schema, tbl,
                  year, semester)
  
  return qry


def qry_course_enhancement_list_2019s2(year, semester, tbl='vw100_courses', schema='course_enhancement'):
  # Returns a dataframe of the courses undergoing enhancement course in year, semester from db (cur)
  qry = " SELECT DISTINCT \n" \
        "   ce.level, ce.school_code, ce.course_code, \n" \
        "   ce.course_code_ces, \n" \
        "   ce.cluster_code, \n" \
        "   cd.school_name, cd.course_name \n" \
        " FROM ( \n" \
        "   SELECT level, school_code, course_code, course_code_ces, cluster_code  \n" \
        "	  FROM {0}.{1} \n" \
        "   WHERE year = {2} AND semester = {3} \n" \
        "       AND cob_selected <> 'True' \n" \
        "       AND la_selected = 'True' \n" \
        "   ) ce \n" \
        " LEFT OUTER JOIN ( \n" \
        "   SELECT * FROM lookups.vw_course_details_recent \n" \
        "   ) cd ON (SPLIT_PART(cd.course_code,'-', 1) = SPLIT_PART(ce.course_code,'-', 1))\n" \
        " ORDER BY ce.school_code, ce.course_code \n" \
        "".format(schema, tbl,
                  year, semester)
  print (qry)
  return qry