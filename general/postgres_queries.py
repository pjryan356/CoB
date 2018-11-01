## EXAMPLES OF USING SAMS HELPER FUNCTIONS
# For Peter August 2018
# Demonstrates the use of the three different connection types
# PUT THE PASSWORD STRING IN

def convert_list_string_for_sql(list1):
  txt = '('
  for str in list1:
    txt += "'{0}', ".format(str)
  # Drop final comma and add )
  txt = txt[:-2]
  txt += ') '
  return txt


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
