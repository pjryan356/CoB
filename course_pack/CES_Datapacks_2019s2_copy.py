import os
import shutil

# Directory containing files
#school = 'GSBL'

source = 'H:\\Projects\\CoB\\CES\\Courses\\2019S2\\{}\\'.format(school)
destination = 'C:\\Users\e35137\\RMIT University\\' \
              'GRP-CoBLearningandTeachingPortfolio - {0} (Shared)\\' \
              'Course Folders ({0})'.format(school)

count = 0
for filename in os.listdir(source):
    if filename.endswith("2019S2.pdf"):
      course_code = filename.split()[0]
      src = os.path.join(source, filename)
      dstpath = '{}\\{}\\'.format(destination, course_code)
      if not os.path.exists(dstpath):
        os.mkdir(dstpath)
        print(dstpath)
      shutil.copy(src, dstpath)
      count += 1
      continue
    else:
      continue

print('Done: {} files copied'.format(count))