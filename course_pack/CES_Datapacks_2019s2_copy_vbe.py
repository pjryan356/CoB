import os
import shutil
import glob
# Directory containing files
school = 'VBE'

source = 'H:\\Projects\\CoB\\CES\\Courses\\2019S2\\{}\\'.format(school)
destination = 'C:\\Users\e35137\\RMIT University\\' \
              'GRP-CoBLearningandTeachingPortfolio - {0} (Shared)\\Program Folders ({0})' \
              ''.format(school)

destination_moved = '{}{}\\'.format(source, 'Moved')

destination_test = source

count = 0

for filename in os.listdir(source):
  fcount = 0
  print('\n\n')
  if filename.endswith("2019S2.pdf"):
    course_code = filename.split()[0]
    print(filename)
    for (dirpath, dirnames, filenames) in os.walk(destination):
      if course_code in dirnames:
        src = os.path.join(source, filename)
        dstpath = '{0}\\{1}\\'.format(dirpath, course_code)
        print(src)
        print(dstpath)
        shutil.copy(src, dstpath)
        fcount += 1
  
    if fcount > 0:
      shutil.move('{}{}'.format(source, filename), '{}{}'.format(destination_moved, filename))
      print('{}{} {} copies'.format(destination_moved, filename, fcount))
  
    else:
      print('Did not find: {}'.format(filename))
    
    
    #course_code = filename.split()[0]
    #src = os.path.join(source, filename)
    #dstpath = '{}\\{}\\'.format(destination, course_code)
    #if not os.path.exists(dstpath):
    #  os.mkdir(dstpath)
    #  print(dstpath)
    #shutil.copy(src, dstpath)
    #count += 1
    continue
  else:
    continue
