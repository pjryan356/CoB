import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')

import general.RMIT_colours as rc

from general.db_helper_functions import (
  connect_to_postgres_db,
  db_extract_query_to_dataframe
)


'''--------------------------------- Connect to Database  ----------------------------'''
# create postgres engine this is the connection to the postgres database
postgres_pw = input("Postgres Password: ")
postgres_user = 'pjryan'
postgres_host = 'localhost'
postgres_dbname = 'postgres'

con_string = "host='{0}' " \
             "dbname='{1}' " \
             "user='{2}' " \
             "password='{3}' " \
             "".format(postgres_host, postgres_dbname, postgres_user, postgres_pw)
con, cur = connect_to_postgres_db(con_string)


for year in range(2014, 2019):
  for sem in [1, 2]:
    for level in ['ve', 'he']:
      qry  = " DROP TABLE IF EXISTS ces_summaries.tbl_{0}_{1}_sem{2} CASCADE; \n".format(level, year, sem)
      print(qry)
      
      qry = " CREATE TABLE ces_summaries.tbl_{0}_{1}_sem{2} \n" \
            " ( \n" \
            '    course_code text COLLATE pg_catalog."default", \n' \
            '    all_flag text COLLATE pg_catalog."default", \n' \
            '    class_nbr text COLLATE pg_catalog."default", \n' \
            '    term_code text COLLATE pg_catalog."default", \n' \
            '    section_code text COLLATE pg_catalog."default", \n' \
            '    course_name text COLLATE pg_catalog."default", \n' \
            '    teaching_staff text COLLATE pg_catalog."default", \n' \
            '    course_coordinator text COLLATE pg_catalog."default", \n' \
            '    career text COLLATE pg_catalog."default", \n' \
            '    survey_population integer, \n' \
            '    osi_response_count integer, \n' \
            '    gts_response_count integer, \n' \
            '    reliability text COLLATE pg_catalog."default", \n' \
            '    campus text COLLATE pg_catalog."default", \n' \
            '    gts numeric, \n' \
            '    gts_mean numeric, \n' \
            '    osi numeric, \n' \
            '    osi_mean numeric, \n' \
            '    international_count integer, \n' \
            '    domestic_count integer, \n' \
            '    ft_count integer, \n' \
            '    pt_count integer, \n' \
            '    gts1 numeric, \n' \
            '    gts2 numeric, \n' \
            '    gts3 numeric, \n' \
            '    gts4 numeric, \n' \
            '    gts5 numeric, \n' \
            '    gts6 numeric \n' \
            ' ) \n' \
            ' WITH ( \n' \
            '    OIDS = FALSE \n' \
            ' ) \n' \
            'TABLESPACE pg_default; \n'.format(level, year, sem)
      print(qry)
      
      qry = " ALTER TABLE ces_summaries.tbl_{0}_{1}_sem{2} \n" \
            " OWNER to postgres; \n".format(level, year, sem)
      print(qry)
      
    
      qry = " COPY ces_summaries.tbl_{0}_{1}_sem{2}( \n" \
            "    course_code, all_flag, class_nbr, term_code, \n" \
            "    section_code, course_name, teaching_staff, course_coordinator, \n" \
            "    career, survey_population, osi_response_count, gts_response_count, \n" \
            "    reliability, campus, gts, gts_mean, osi, osi_mean, international_count, \n" \
            "    domestic_count, ft_count, pt_count, gts1, gts2, gts3, gts4, gts5, gts6 \n" \
            "   ) \n" \
            " FROM 'C:\Peter\CoB\CES\whole_college_summaries\csv\{1}_{3}_sem{2}.csv' delimiter ',' csv header; \n " \
            "".format(level, year, sem, level.upper())
      print(qry)
    
qry = " CREATE OR REPLACE VIEW ces_summaries.vw_summaries_combined AS \n" \
      "   SELECT t2.* \n" \
      "   FROM ( \n"

for year in range(2014, 2019):
  for sem in [1, 2]:
    for level in ['ve', 'he']:
      qry += "      SELECT  \n" \
             "        '{0}'::text AS survey_year, \n" \
             "        {1}::integer AS survey_semester, \n" \
             "        '{2}'::text AS survey_level, \n" \
             "        t1.* \n" \
             "      FROM ces_summaries.tbl_{3}_{0}_sem{1} t1\n" \
             "      UNION \n".format(year, sem, level.upper(), level)
qry = qry[:-10]
qry += "    ) t2; \n"
print(qry)
#db_extract_query_to_dataframe(qry, cur, print_messages=False)


qry = " CREATE OR REPLACE VIEW ces_summaries.vw_teacher_performance_post_2014 AS \n" \
      "   SELECT  \n" \
      "     sc.teaching_staff,  \n" \
      "     count(sc.gts) AS classes, \n" \
      "     count(sc.gts) FILTER (WHERE sc.gts < 75::numeric) AS gts_classes_less_than_75, \n" \
      "     count(sc.gts) FILTER (WHERE sc.gts < 50::numeric) AS gts_classes_less_than_50,  \n" \
      "     count(sc.gts) FILTER (WHERE sc.gts >= 50::numeric AND sc.gts < 60::numeric) AS gts_classes_50, \n" \
      "     count(sc.gts) FILTER (WHERE sc.gts >= 60::numeric AND sc.gts < 70::numeric) AS gts_classes_60, \n" \
      "     count(sc.gts) FILTER (WHERE sc.gts >= 70::numeric AND sc.gts < 80::numeric) AS gts_classes_70, \n" \
      "     count(sc.gts) FILTER (WHERE sc.gts >= 80::numeric AND sc.gts < 90::numeric) AS gts_classes_80, \n" \
      "     count(sc.gts) FILTER (WHERE sc.gts >= 90::numeric) AS gts_classes_90 \n" \
      "   FROM ces_summaries.vw_summaries_combined sc \n" \
      "   WHERE sc.survey_year >= '2015'::text AND sc.term_code > '1500'::text \n" \
      "   GROUP BY sc.teaching_staff; \n"
print(qry)
#db_extract_query_to_dataframe(qry, cur, print_messages=False)


qry = " CREATE OR REPLACE VIEW ces_summaries.vw_teacher_performance_by_year AS \n" \
      "   SELECT sc.teaching_staff, \n" \
      "     count(sc.gts) FILTER (WHERE sc.survey_year >= '2015'::text) AS classes_post_2014, \n" \
      "     count(sc.gts) FILTER (WHERE sc.gts < 75::numeric AND sc.survey_year >= '2015'::text) AS classes_post_2014_gts_less_than_75, \n" \
      "     count(sc.gts) FILTER (WHERE sc.gts < 50::numeric AND sc.survey_year >= '2015'::text) AS classes_post_2014_gts_less_than_50"

for year in range(2015, 2019):
  qry += "    , \n" \
         "    count(sc.gts) FILTER (WHERE sc.survey_year = '{0}'::text) AS classes_{0}, \n" \
         "    count(sc.gts) FILTER (WHERE sc.gts < 75::numeric AND sc.survey_year = '{0}'::text) AS classes_{0}_gts_less_than_75, \n" \
         "    count(sc.gts) FILTER (WHERE sc.gts < 50::numeric AND sc.survey_year = '{0}'::text) AS classes_{0}_gts_less_than_50 " \
         "".format(year)
  
qry +=  "  \nFROM ces_summaries.vw_summaries_combined sc \n" \
        "  GROUP BY sc.teaching_staff; \n"
print(qry)
#db_extract_query_to_dataframe(qry, cur, print_messages=False)


'''
CREATE OR REPLACE VIEW ces_summaries.teacher_performance_by_year_percentage AS
 SELECT vw_teacher_performance_by_year.teaching_staff,
    vw_teacher_performance_by_year.classes_post_2014,
        CASE
            WHEN vw_teacher_performance_by_year.classes_post_2014 = 0 THEN NULL::numeric
            ELSE round(100.0 * vw_teacher_performance_by_year.classes_post_2014_gts_less_than_75::numeric / vw_teacher_performance_by_year.classes_post_2014::numeric, 1)
        END AS classes_post_2014_lt_75,
        CASE
            WHEN vw_teacher_performance_by_year.classes_post_2014 = 0 THEN NULL::numeric
            ELSE round(100.0 * vw_teacher_performance_by_year.classes_post_2014_gts_less_than_50::numeric / vw_teacher_performance_by_year.classes_post_2014::numeric, 1)
        END AS classes_post_2014_lt_50,
    vw_teacher_performance_by_year.classes_2015,
        CASE
            WHEN vw_teacher_performance_by_year.classes_2015 = 0 THEN NULL::numeric
            ELSE round(100.0 * vw_teacher_performance_by_year.classes_2015_gts_less_than_75::numeric / vw_teacher_performance_by_year.classes_2015::numeric, 1)
        END AS classes_2015_lt_75,
        CASE
            WHEN vw_teacher_performance_by_year.classes_2015 = 0 THEN NULL::numeric
            ELSE round(100.0 * vw_teacher_performance_by_year.classes_2015_gts_less_than_50::numeric / vw_teacher_performance_by_year.classes_2015::numeric, 1)
        END AS classes_2015_lt_50,
    vw_teacher_performance_by_year.classes_2016,
        CASE
            WHEN vw_teacher_performance_by_year.classes_2016 = 0 THEN NULL::numeric
            ELSE round(100.0 * vw_teacher_performance_by_year.classes_2016_gts_less_than_75::numeric / vw_teacher_performance_by_year.classes_2016::numeric, 1)
        END AS classes_2016_lt_75,
        CASE
            WHEN vw_teacher_performance_by_year.classes_2016 = 0 THEN NULL::numeric
            ELSE round(100.0 * vw_teacher_performance_by_year.classes_2016_gts_less_than_50::numeric / vw_teacher_performance_by_year.classes_2016::numeric, 1)
        END AS classes_2016_lt_50,
    vw_teacher_performance_by_year.classes_2017,
        CASE
            WHEN vw_teacher_performance_by_year.classes_2017 = 0 THEN NULL::numeric
            ELSE round(100.0 * vw_teacher_performance_by_year.classes_2017_gts_less_than_75::numeric / vw_teacher_performance_by_year.classes_2017::numeric, 1)
        END AS classes_2017_lt_75,
        CASE
            WHEN vw_teacher_performance_by_year.classes_2017 = 0 THEN NULL::numeric
            ELSE round(100.0 * vw_teacher_performance_by_year.classes_2017_gts_less_than_50::numeric / vw_teacher_performance_by_year.classes_2017::numeric, 1)
        END AS classes_2017_lt_50,
    vw_teacher_performance_by_year.classes_2018,
        CASE
            WHEN vw_teacher_performance_by_year.classes_2018 = 0 THEN NULL::numeric
            ELSE round(100.0 * vw_teacher_performance_by_year.classes_2018_gts_less_than_75::numeric / vw_teacher_performance_by_year.classes_2018::numeric, 1)
        END AS classes_2018_lt_75,
        CASE
            WHEN vw_teacher_performance_by_year.classes_2018 = 0 THEN NULL::numeric
            ELSE round(100.0 * vw_teacher_performance_by_year.classes_2018_gts_less_than_50::numeric / vw_teacher_performance_by_year.classes_2018::numeric, 1)
        END AS classes_2018_lt_50
   FROM ces_summaries.vw_teacher_performance_by_year;

ALTER TABLE ces_summaries.teacher_performance_by_year_percentage
    OWNER TO postgres;
'''