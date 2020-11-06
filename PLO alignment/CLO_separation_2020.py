## Creates course assessment files for CAC purposes
# Peter Ryan Nov 2018

import pandas as pd
import sys
import re
import os
import psycopg2
from sqlalchemy import (create_engine, orm)
from tabulate import tabulate

sys.path.append('c:\\Peter\\GitHub\\CoB\\')

# Create connections
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


def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def get_CLOs(text, type='Good'):
  clo_list = []
  if type == 'Good':
    CLOs = re.split('CLO|CL0|<li>|</li>|<p>|</p>|<div>|</div>', text)
    for clo in CLOs:
      clo = clo.replace('<br />', '\n')
      clo = clo.replace("’", "'")
      clo = clo.strip()
      clo = clo.rstrip()
      clo = clo.strip('-')
      if re.search('[0-9]', clo):
        clo = cleanhtml(clo)
        clo = clo.replace('<br />', '\n')
        clo = clo.replace("’", "'")
        clo = clo.strip()
        clo = clo.rstrip()
        clo = clo.strip('1')
        clo = clo.strip('2')
        clo = clo.strip('3')
        clo = clo.strip('4')
        clo = clo.strip('5')
        clo = clo.strip('6')
        clo = clo.strip('7')
        clo = clo.strip('8')
        clo = clo.strip('9')
        clo = clo.strip('0')
        clo = clo.strip('0')
        clo = clo.strip('1')
        clo = clo.strip('2')
        clo = clo.strip('3')
        clo = clo.strip('4')
        clo = clo.strip('5')
        clo = clo.strip('6')
        clo = clo.strip('7')
        clo = clo.strip('8')
        clo = clo.strip('9')
        clo = clo.strip('0')
        clo = clo.strip('.\xa0')
        clo = clo.strip()
        clo = clo.rstrip()
        clo = clo.rstrip('and')
        clo = clo.strip()
        clo = clo.rstrip()
        clo = clo.strip(';')
        clo = clo.strip(':')
        clo = clo.strip()
        clo = clo.rstrip()
        if len(clo) > 10:
          clo_list.append(clo)
        
  if type == 'Dot':
    CLOs = re.split('<li>|</li>|<p>|</p>|<div>|</div>|<br />|</p>|<p>|<br /> ', text)
    for clo in CLOs:
      clo = clo.replace('<br />', '\n')
      clo = clo.replace("’", "'")
      clo = clo.strip()
      clo = clo.rstrip()
      clo = cleanhtml(clo)
      clo = clo.strip()
      clo = clo.rstrip()
      if (re.match('• ', clo) or
        re.match('• ', clo) or
        re.match('- ', clo) or
        re.match('[a-z]. ', clo)):
        
        if re.match('[a-z]. ', clo):
          m = re.match('[a-z]. ', clo)
          clo = clo.strip(m.group(0))
          
        clo = clo.strip('• ')
        clo = clo.strip('• ')
        clo = clo.strip('- ')
        clo = clo.rstrip("^a.")
        clo = clo.rstrip('b. ')
        clo = clo.rstrip('c. ')
        clo = clo.rstrip('d. ')
        clo = clo.rstrip('e. ')
        clo = clo.rstrip('f. ')
        clo = clo.rstrip('g. ')
        clo = clo.rstrip('h. ')
        clo = clo.rstrip('i. ')
        clo = cleanhtml(clo)
        clo = clo.replace('<br />', '\n')
        clo = clo.replace("’", "'")
        clo = clo.strip()
        clo = clo.rstrip()
        clo = clo.strip('.\xa0')
        clo = clo.strip()
        clo = clo.rstrip()
        clo = clo.rstrip('and')
        clo = clo.strip()
        clo = clo.rstrip()
        clo = clo.strip(';')
        clo = clo.strip(':')
        clo = clo.strip()
        clo = clo.rstrip()
        if len(clo) > 10:
          clo_list.append(clo)
      
      
  if type == 'Num':
    CLOs = re.split('<li>|</li>|<p>|</p>|<div>|</div>|<br />|<br />', text)
    for clo in CLOs:
      clo = clo.replace('<br />', '\n')
      clo = clo.replace("’", "'")
      clo = clo.strip()
      clo = clo.rstrip()
      clo = clo.strip('-')
      clo = cleanhtml(clo)
      clo = clo.strip()
      clo = clo.rstrip()
      if re.match('[1-9].', clo):
        clo = cleanhtml(clo)
        clo = clo.replace('<br />', '\n')
        clo = clo.replace("’", "'")
        clo = clo.strip()
        clo = clo.rstrip()
        clo = clo.strip('1')
        clo = clo.strip('2')
        clo = clo.strip('3')
        clo = clo.strip('4')
        clo = clo.strip('5')
        clo = clo.strip('6')
        clo = clo.strip('7')
        clo = clo.strip('8')
        clo = clo.strip('9')
        clo = clo.strip('0')
        clo = clo.strip('0')
        clo = clo.strip('1')
        clo = clo.strip('2')
        clo = clo.strip('3')
        clo = clo.strip('4')
        clo = clo.strip('5')
        clo = clo.strip('6')
        clo = clo.strip('7')
        clo = clo.strip('8')
        clo = clo.strip('9')
        clo = clo.strip('0')
        clo = clo.strip('.\xa0')
        clo = clo.strip()
        clo = clo.rstrip()
        clo = clo.rstrip('and')
        clo = clo.strip()
        clo = clo.rstrip()
        clo = clo.strip(';')
        clo = clo.strip(':')
        clo = clo.strip()
        clo = clo.rstrip()
        if len(clo) > 10:
          clo_list.append(clo)

  if type == 'List':
    CLOs = re.split('<li>|</li>|<p>|</p>|<div>|</div>|<br />|', text)
    for clo in CLOs:
      clo = cleanhtml(clo)
      if 'Every placement is different,' in clo:
        return ['']
      if (len(clo) > 10 and
          re.search("course you will able to:", clo) == None and
          re.search("you will be able to:", clo) == None and
          re.search("you should be able to:", clo) == None and
          re.search("completion of this course", clo) == None and
          re.search("Learning Outcome", clo) == None and
          re.search("Learning outcome", clo) == None and
          re.search("learning outcome", clo) == None and
          re.search("engage in activities leading to an understanding of", clo) == None and
          re.search("Enabling Knowledge and Skills for Capabilities", clo) == None and
          re.search("Learning Objective", clo) == None and
          re.search("enable you to develop your:", clo) == None ):
          clo_list.append(clo)
    '''

    else:
      NotOKlist = ['<p>', '</p>', '<br>', '<br />', '</br>', '<div>', '</div>','CLO']
      if any(s in text for s in NotOKlist):
        CLOs = re.split('<br>|<br />|</p>|<p>|</br>|CLO|<div>|</div>', text)
      else:
        return [text]
      
      CLOs_2 = []
      for clo in CLOs:
        clo = clo.replace('<br />', '\n')
        clo = cleanhtml(clo)
        try:
          clo = clo.strip()
          clo = clo.rstrip()
          clo = clo.strip('-')
          clo = clo.strip('•')
          clo = clo.strip('*')
          clo = clo.strip('1')
          clo = clo.strip('2')
          clo = clo.strip('3')
          clo = clo.strip('4')
          clo = clo.strip('5')
          clo = clo.strip('6')
          clo = clo.strip('7')
          clo = clo.strip('8')
          clo = clo.strip('9')
          clo = clo.strip('0')
          clo = clo.strip('.')
          if clo.startswith(":"):
            clo =  clo[1:]
          clo = clo.strip(')')
          clo = clo.strip('\uf0a7')
          clo = clo.strip()
        except Exception as e:
          print(cid)
          print(e)
          pass
        
        if len(clo) > 10:
          CLOs_2.append(clo)

    if len(CLOs_2) == 1:
      return CLOs_2
    
    while ':' in CLOs_2[0][-4:]:
      CLOs_2 = CLOs_2[1:]
      

    
    

    if 'Enabling Knowledge and Skills for Capabilities' in CLOs_2[0]:
      CLOs_2 = CLOs_2[1:]
    
    return CLOs_2
  
  except Exception as e:
    print(cid)
    print(e)
    print(text, '\n')
    return['']
  '''
  return clo_list



# open CLOs worksheet
directory = 'C:\\Peter\\CLOs 2020\\'
clo_filename = 'CLOs.xlsx'
master_list = []

'''
## Good
clo_df = pd.read_excel(open(directory+clo_filename, 'rb'), "CLO (Good)", converters={'course_id': str})
for i, r in clo_df.iterrows():
  CLO_list = get_CLOs(r['learning_outcomes'], 'Good')
  k = 1
  for clo in CLO_list:
    master_list.append([r['course_id'], k, clo, r['sys_updated_on'].date()])
    k += 1

## Alt
clo_df = pd.read_excel(open(directory+clo_filename, 'rb'), "CLO (Alt)", converters={'course_id': str})
for i, r in clo_df.iterrows():
  CLO_list = get_CLOs(r['learning_outcomes'], 'Good')
  k = 1
  for clo in CLO_list:
    master_list.append([r['course_id'], k, clo, r['sys_updated_on'].date()])
    k += 1

## Numbered
clo_df = pd.read_excel(open(directory+clo_filename, 'rb'), "Numbered", converters={'course_id': str})
for i, r in clo_df.iterrows():
  CLO_list = get_CLOs(r['learning_outcomes'], 'Num')
  k = 1
  for clo in CLO_list:
    master_list.append([r['course_id'], k, clo, r['sys_updated_on'].date()])
    k += 1

## Dot
clo_df = pd.read_excel(open(directory + clo_filename, 'rb'), "Dot", converters={'course_id': str})
for i, r in clo_df.iterrows():
  CLO_list = get_CLOs(r['learning_outcomes'], 'Dot')
  k = 1
  for clo in CLO_list:
    master_list.append([r['course_id'], k, clo, r['sys_updated_on'].date()])
    k += 1

## List
clo_df = pd.read_excel(open(directory + clo_filename, 'rb'), "List", converters={'course_id': str})
for i, r in clo_df.iterrows():
  CLO_list = get_CLOs(r['learning_outcomes'], 'List')
  k = 1
  if len(CLO_list) < 10:
    for clo in CLO_list:
      master_list.append([r['course_id'], k, clo, r['sys_updated_on'].date()])
      k += 1
  #else:
    #print('\n\n')
    #print(r['course_id'], r['sys_updated_on'])
    #for clo in CLO_list:
      #print(clo)
'''

## Complex
clo_df = pd.read_excel(open(directory + clo_filename, 'rb'), "More", converters={'course_id': str})
for i, r in clo_df.iterrows():
  print(i, r['course_id'], r['learning_outcomes'])
  CLO_list = get_CLOs(r['learning_outcomes'], 'List')
  k = 1
  if len(CLO_list) < 10:
    for clo in CLO_list:
      master_list.append([r['course_id'], k, clo, r['sys_updated_on'].date()])
      k += 1
  #else:
    #print('\n\n')
    #print(r['course_id'], r['sys_updated_on'])
    #for clo in CLO_list:
      #print(clo)

df = pd.DataFrame(master_list, columns = ['course_id', 'clo_nbr', 'clo_text', 'updated'])
df['course_id'] = df['course_id'].apply(lambda x: x.zfill(6))

print(tabulate(df, headers='keys'))


df.to_sql(name='tbl_clo',
            con=postgres_engine,
            schema='courses',
            if_exists='append',
            index=False
          )

