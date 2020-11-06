## Helper functions for distributing files
# Peter Ryan Jan 2020

import shutil
import os

def distribute_files(
  source_folder,
  file_deliminator=' ', school_position=0, course_code_position=0,
  school=False, course_code=False):
  '''
  Copy files into Course OneDrive folders within School OneDrive
    source_folder: folder containing files to be distributed
    file_deliminator: deliminator to break filenames apart
    school_position: position of school in filename
    course_code_position: position of course_code in filename
    school: False if in filename
    course_code: False if in filename
  '''
  
  # Ensure Moved folder exists in source folder to store moved files
  #   this allowed undistributed files to be recognised as they remain in place.
  destination_moved = '{}{}\\'.format(source_folder, 'Moved')
  if not os.path.exists(destination_moved):
    os.mkdir(destination_moved)
  
  count_moved = 0
  count_unmoved = 0
  # Loop through files in source directory
  for filename in os.listdir(source_folder):
    
    if '.xlsx' in filename:
      fname = filename.split('.')[0]
      found = False
  
      copyname = filename
      
      if school == False:
        # Get school from filename
        school = fname.split(file_deliminator)[school_position]
        
        # Remove school from copy filename
        copyname = filename.replace('{} '.format(school), '')
        
      if course_code == False:
        # Get course_code from filename
        course_code = fname.split(file_deliminator)[course_code_position]
        print(course_code)
      # Destination is the school OneDrive folders
      #  VBE has a different folder structure to tother schools
      #    Course folders are within Program Folders
      destination = 'C:\\Users\e35137\\RMIT University\\' \
                    'GRP-CoBLearningandTeachingPortfolio - {0} (Shared)\\Course Folders ({0})\\' \
                    ''.format(school)
      
      if school == 'VBE':
        destination = 'C:\\Users\e35137\\RMIT University\\' \
                      'GRP-CoBLearningandTeachingPortfolio - {0} (Shared)\\Program Folders ({0})\\' \
                      ''.format(school)
  
          
      # Loop through folders in destination folder to find course_code folder
      for (dirpath, dirnames, filenames) in os.walk(destination):
        if course_code in dirnames:
          # Copy file into correct directory
          src = os.path.join(source_folder, filename)
          dst_folder = '{0}\\{1}\\2020 response\\'.format(dirpath, course_code)
          if not os.path.exists(dst_folder):
            os.mkdir(dst_folder)
  
          dstpath = '{}{}'.format(dst_folder, copyname)
          shutil.copy(src, dstpath)
          
          # Move copied file into Moved directory
          shutil.move('{}{}'.format(source_folder, filename), '{}{}'.format(destination_moved, filename))
          found = True
          print(dstpath)
          course_code = False
          break
          
        else:
          continue
      
      if found:
        count_moved += 1
      else:
        count_unmoved += 1
    

      
    
  return [count_moved, count_unmoved]



source_folder = 'C:\\Users\\e35137\\RMIT University\\GRP-CoBLearningandTeachingPortfolio - 2020_response\\'

source_folder += 'Action Plans\\Management\\'

'''
distribute_files(
  source_folder,
  file_deliminator=' ',
  school='MGT',
  course_code_position=3)

'''