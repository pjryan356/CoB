## Helper functions for distributing files
# Peter Ryan Jan 2020

import shutil
import os

def distribute_files(
  source_folder,
  file_deliminator=' ', school_position=0, course_code_position=0,
  school_known=False, course_code_known=False):
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
    print(filename)
    found = False
    if '.pdf' not in filename:
      continue
    if school_known == False:
      # Get school from filename
      school = filename.split(file_deliminator)[school_position]
      
      # Remove school from copy filename
      copyname = filename.replace('{} '.format(school), '')
    else:
      school = school_known
      
    if course_code_known == False:
      # Get course_code from filename
      course_code = filename.split(file_deliminator)[course_code_position]
    else:
      course_code = course_code_known
    # Destination is the school OneDrive folders
    #  VBE has a different folder structure to to the schools
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
        dstpath = '{0}\\{1}\\{2}'.format(dirpath, course_code, copyname)
        print(src)
        print(dstpath)
        shutil.copy(src, dstpath)

        # Move copied file into Moved directory
        shutil.move('{}{}'.format(source_folder, filename), '{}{}'.format(destination_moved, filename))
        found = True
        break
        
      else:
        continue
    
    if found:
      count_moved += 1
    else:
      count_unmoved += 1
      
    
  return [count_moved, count_unmoved]


def copy_rename(old_file_name, new_file_name):
  src_dir = os.curdir
  dst_dir = os.path.join(os.curdir, "subfolder")
  src_file = os.path.join(src_dir, old_file_name)
  shutil.copy(src_file, dst_dir)
  
  dst_file = os.path.join(dst_dir, old_file_name)
  new_dst_file_name = os.path.join(dst_dir, new_file_name)
  os.rename(dst_file, new_dst_file_name)


folder = 'H:\\Projects\\CoB\\CES\\Course Enhancement\\2020 S1\\DataPacks\\VBE\\'
distribute_files(
  folder,
  file_deliminator=' ', school_position=0, course_code_position=1,
  school_known=False, course_code_known=False)