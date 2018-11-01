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


def qry_get_course_id_for_course_codes(crsList, st_term, end_term):
  qry  = '''
SELECT DISTINCT
        cls.CRSE_ID AS course_id,
        cls.SUBJECT | | cls.CATALOG_NBR AS course_code_ms,
        cls.CAMPUS AS campus_ms
      FROM ps_class_tbl cls
      WHERE strm > '{0}' AND strm < '{1}'
          AND cls.location <> 'WWW'
          AND cls.SUBJECT | | cls.CATALOG_NBR IN {2}
      GROUP BY cls.CRSE_ID, cls.SUBJECT | | cls.CATALOG_NBR, cls.CAMPUS
  '''.format(st_term, end_term, convert_list_string_for_sql(crsList))
  return qry
  
def qry_get_course_code_locations_for_course_id(st_term, end_term):
  qry = '''
      SELECT 	cls.CRSE_ID AS course_id,
        cls.SUBJECT || cls.CATALOG_NBR AS course_code,
        cls.DESCR AS course_name,
        cls.CAMPUS,
        cls.LOCATION
      FROM PS_CLASS_TBL cls
      WHERE strm > '{0}' AND strm < '{1}'
      AND STRM =
            (SELECT MAX(maxcls.STRM) FROM PS_CLASS_TBL maxcls
             WHERE cls.crse_id = maxcls.crse_id
              AND cls.SUBJECT || cls.CATALOG_NBR = maxcls.SUBJECT || cls.CATALOG_NBR
              AND cls.CAMPUS = maxcls.CAMPUS
              AND cls.LOCATION = maxcls.LOCATION)
      GROUP BY  cls.CRSE_ID, cls.SUBJECT || cls.CATALOG_NBR, cls.DESCR, cls.CAMPUS, cls.LOCATION
  '''.format(st_term, end_term)
  return qry

def qry_sams_course_locations(crsList=None, st_term='1800', end_term='2000'):
  crsList = ['ACCT1028', 'ACCT1046', 'ACCT1056', 'ACCT1060', 'ACCT1064', 'ACCT1077', 'ACCT2189', 'ACCT2213', 'ACCT2228',
             'ACCT2267', 'ACCT2271', 'ACCT2275', 'ACCT2277', 'ACCT5371C', 'ACCT5372C', 'ACCT5380C', 'ACCT5381C', 'ACCT5391C',
             'ACCT5393C', 'ACCT5394C', 'BAFI1002',
  'BAFI1018', 'BAFI1026', 'BAFI1042', 'BAFI1070', 'BAFI2081', 'BAFI5210C', 'BAFI5211C', 'BAFI5212C', 'BAFI5213C',
  'BAFI5215C',
  'BAFI5220C', 'BAFI5221C', 'BUSM1074', 'BUSM1080', 'BUSM1094', 'BUSM1162', 'BUSM1222', 'BUSM1313', 'BUSM1534',
  'BUSM1539', 'BUSM3115',
  'BUSM3119', 'BUSM3122', 'BUSM3125', 'BUSM3323', 'BUSM4052', 'BUSM4054', 'BUSM4095', 'BUSM4141', 'BUSM4160',
  'BUSM4176', 'BUSM4177',
  'BUSM4295', 'BUSM4323', 'BUSM4360', 'BUSM4361', 'BUSM4367', 'BUSM4369', 'BUSM4371', 'BUSM4372', 'BUSM4377',
  'BUSM4379', 'BUSM4380',
  'BUSM4448', 'BUSM4495', 'BUSM4496', 'BUSM4528', 'BUSM4531', 'BUSM4534', 'BUSM4546', 'BUSM4550', 'BUSM4558',
  'BUSM4583', 'BUSM4688',
  'BUSM7932C', 'BUSM7938C', 'COMM7332C', 'COMM7333C', 'COSC6188C', 'COSC7357C', 'COSC7358C', 'COSC7359C', 'COSC7360C',
  'COSC7362C',
  'COSC7365C', 'COSC7373C', 'COSC7374C', 'ECON1020', 'ECON1030', 'ECON1042', 'ECON1066', 'ECON1082', 'ECON1086',
  'ECON1223', 'ECON1238',
  'ECON1246', 'ECON1247', 'ECON1248', 'ECON1273', 'ECON1275', 'EMPL7068C', 'EMPL7070C', 'EMPL7076C', 'GRAP5370C',
  'INTE1002', 'INTE1030',
  'INTE1063', 'INTE2043', 'INTE2489', 'ISYS1039', 'ISYS1168', 'ISYS2056', 'ISYS2395', 'ISYS2396', 'ISYS2427',
  'ISYS2452', 'ISYS3314',
  'ISYS3374', 'JUST5748', 'JUST5749', 'JUST5750', 'LAW1019', 'LAW1023', 'LAW1024', 'LAW1028', 'LAW2395', 'LAW2442',
  'LAW2453', 'LAW2457',
  'LAW2477', 'LAW2486', 'LAW2487', 'LAW2488', 'LAW2490', 'LAW2492', 'LAW2493', 'LAW2494', 'LAW2496', 'LAW2524',
  'LAW2538', 'LAW2540',
  'LAW2551', 'LAW5716', 'LAW5717', 'LAW5719', 'LAW5720', 'LAW5721', 'LAW5724', 'LAW5730C', 'LAW5732C', 'LIBR1028',
  'LIBR1070', 'MATH5332C',
  'MKTG1041', 'MKTG1045', 'MKTG1048', 'MKTG1050', 'MKTG1053', 'MKTG1061', 'MKTG1071', 'MKTG1080', 'MKTG1086',
  'MKTG1092', 'MKTG1104',
  'MKTG1126', 'MKTG1215', 'MKTG1276', 'MKTG1296', 'MKTG1329', 'MKTG1415', 'MKTG1423', 'MKTG6045C', 'MKTG7878',
  'MKTG7881', 'MKTG7887C',
  'MKTG7888C', 'MKTG7896', 'MKTG7911C', 'MKTG7913C', 'MKTG7929C', 'MKTG7943C', 'MKTG7947C', 'MKTG7977C', 'OFFC5328C',
  'OHTH5867C',
  'OHTH5872C', 'OMGT1053', 'OMGT1058', 'OMGT1070', 'OMGT2155', 'OMGT2190', 'OMGT2243', 'OMGT2295', 'OMGT5034',
  'OMGT5039C', 'POLI5044C',
  'ECON1268', 'LAW2447', 'BAFI3184', 'ECON1194', 'BAFI3192', 'ACCT2160', 'ACCT2105', 'BAFI3182', 'ACCT2126',
  'ACCT2158', 'LAW2485', 'BUSM2416',
  'BUSM4529', 'BUSM3244', 'BUSM4532', 'BUSM4488', 'BUSM4155', 'BUSM2412', 'BUSM4161', 'MKTG1205', 'BUSM4374',
  'BUSM4561', 'BUSM3311', 'ISYS2109',
  'SOCU2264', 'BUSM4557', 'BUSM3097', 'OMGT2085', 'ISYS2110', 'BUSM4092', 'BUSM3299']

  crsList = ['ACCT1028', 'ACCT1046']
  qry = '''
  SELECT *
  FROM (
    SELECT DISTINCT
      t1.course_id, t1.course_code_ms, t1.campus_ms, campus, course_code
    FROM ({0}) t1
    LEFT OUTER JOIN ({1}) t2
    ON t1.course_id = t2.course_id
  )
  pivot(
    max(course_code)
    for campus in ('AUSCY' city, 'AUSBR' brunswick, 'AUSBU' bundoora, 'AUSOL' aus_online,
    'SGPIM' singapore_im, 'SGPKP' singapore_kp, 'CHNSI' china_shanghai,
    'CHNBJ' china_beijing, 'HKGAC' hongkong_ac, 'HKGVT' hongkong_vt,
    'AUSVN' AUSVN, 'VNMRI' veitnam_ri, 'VNMPA' veitnam_pa,
    'VNMRH' veitnam_rh, 'IDNUP' uph, 'ONLOU' www_ou, 'ONLKP' www_kp)
  )
  '''.format(qry_get_course_id_for_course_codes(crsList, st_term, end_term),
             qry_get_course_code_locations_for_course_id(st_term, end_term))
  return qry


def qry_std_class_grades(st_term='1700', end_term='1900'):
  qry = '''
SELECT DISTINCT
   enrl.STRM || '-' || enrl.CLASS_NBR || '-' || cls.SUBJECT || cls.CATALOG_NBR AS classkey,
   enrl.STRM AS term_code,
   cls.SUBJECT || cls.CATALOG_NBR AS course_code,
   substr(enrl.EMPLID,1,7) as std_id,
   enrl.ACAD_PROG AS program_code,
   enrl.STDNT_ENRL_STATUS AS enrl_status,
   enrl.ENRL_STATUS_REASON AS enrl_reason,
   enrl.CRSE_GRADE_OFF AS course_grade,
   enrl.CRSE_GRADE_INPUT AS course_mark,
   enrl.GRD_PTS_PER_UNIT AS course_grade_points_per_unit,
   enrl.GRADE_POINTS AS course_grade_points,
   enrl.INCLUDE_IN_GPA AS include_in_gpa,
   enrl.UNT_TAKEN AS course_units,
   enrl.EARN_CREDIT AS earn_credit,
   enrl.GRADING_BASIS_ENRL AS grading_basis
 FROM
   PS_STDNT_ENRL enrl,
   PS_ACAD_PROG_TBL prg,
   PS_CLASS_TBL cls
 WHERE
     enrl.strm > '{0}' AND enrl.strm < '{1}'
   AND enrl.ACAD_PROG = prg.ACAD_PROG
   AND enrl.STRM = cls.STRM
   AND enrl.CLASS_NBR = cls.CLASS_NBR
   AND enrl.INSTITUTION = prg.INSTITUTION
   AND prg.EFFDT = (
         SELECT MAX(prg_ed.EFFDT)
         FROM PS_ACAD_PROG_TBL prg_ed
         WHERE prg.INSTITUTION = prg_ed.INSTITUTION
           AND prg.ACAD_PROG = prg_ed.ACAD_PROG
           AND prg_ed.EFFDT <= SYSDATE)
  '''.format(st_term, end_term)
  return qry

def qry_course_program_enrolments(st_term='1300', end_term='1900'):
  qry = '''
SELECT
  enrl.term_code,
  enrl.course_code,
  enrl.program_code,
  enrl.enrl_status,
  enrl.enrl_reason,
  count(DISTINCT enrl.std_id) AS population
FROM  (
    {0}
    ) enrl
GROUP BY enrl.term_code, enrl.course_code, enrl.program_code, enrl.enrl_status, enrl.enrl_reason
'''.format(qry_std_class_grades(st_term=st_term, end_term=end_term))
  return qry

def qry_course_details(st_term='1700', end_term='1900'):
  qry = '''
SELECT DISTINCT
	cl.subject||cl.catalog_nbr AS course_code,
	cl.descr AS course_name,
	cl.strm AS term_code,
	cl.acad_career,
	cl.acad_org AS school_code,
	sch.descr AS school_name,
	CASE WHEN cl.acad_group = 'SET' THEN 'SEH'
		ELSE cl.acad_group END AS college,
	cl.campus,
	term.descrshort AS term_description,
	term.acad_year
FROM ps_class_tbl cl
INNER JOIN ps_term_tbl term ON (cl.strm = term.strm AND cl.acad_career = term.acad_career)
INNER JOIN (
	SELECT
		acad_org,
		descr,
		effdt
	FROM  ps_acad_org_tbl t1
	WHERE EFF_STATUS = 'A' AND effdt = (SELECT max(effdt) FROM ps_acad_org_tbl tmax WHERE tmax.acad_org = t1.acad_org AND tmax.eff_status = t1.eff_status)
	) sch ON ( sch.acad_org = cl.acad_org)
WHERE
  cl.strm > '{0}' AND cl.strm < '{1}'
'''.format(st_term, end_term)
  return qry

def qry_program_details():
  qry = '''
SELECT
	prg1.acad_prog AS program_code,
 	CASE WHEN prg1.acad_group = 'SET' THEN 'SEH' ELSE prg1.acad_group END AS college,
 	prg1.acad_org AS school_code,
 	sch.school_name,
 	prg1.acad_career,
 	COALESCE(prg3.diploma_descr, prg1.program_name) AS program_name,
 	prg1.program_status
FROM (
	SELECT
		acad_prog,
		acad_plan,
		acad_group,
		acad_org,
		acad_career,
		CASE
			WHEN EFF_STATUS = 'A' THEN 'OPEN'
			WHEN EFF_STATUS = 'I' THEN 'DISC'
			ELSE 'UKN' END AS program_status,
        descr AS program_name,
   		eff_status
	FROM  PS_ACAD_PROG_TBL t1
	WHERE t1.effdt = (SELECT max(effdt) FROM PS_ACAD_PROG_TBL maxt WHERE t1.acad_prog = maxt.acad_prog)
	  AND t1.effdt > '31 DEC 2000'
	) prg1

LEFT OUTER JOIN (
	SELECT DISTINCT
		*
	FROM PS_ACAD_PLAN_TBL t1
	WHERE t1.EFFDT = (SELECT max(effdt)
						FROM PS_ACAD_PLAN_TBL maxt
						WHERE t1.acad_prog = maxt.acad_prog
							AND t1.acad_plan = maxt.acad_plan)
	) prg3  ON (prg1.acad_plan=prg3.acad_plan
				AND prg1.acad_career=prg3.acad_career
				AND prg1.acad_prog=prg3.acad_prog)
LEFT OUTER JOIN (
	SELECT t1.acad_org, t1.descr AS school_name, t1.effdt
	FROM PS_ACAD_ORG_TBL t1
	WHERE t1.EFF_STATUS = 'A'
			AND t1.effdt = (SELECT max(effdt) FROM PS_ACAD_ORG_TBL maxt WHERE maxt.acad_org = t1.acad_org)
	) sch ON prg1.acad_org = sch.acad_org
WHERE  prg1.acad_group IN ('SET', 'TRAIN', 'RMITU', 'DSC', 'SEH', 'RMITV', 'BUS')
  '''
  return qry
