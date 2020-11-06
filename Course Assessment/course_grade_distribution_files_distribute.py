## Copys grade distribution files into seperate shared OneDrive folders
# Peter Ryan Jan 2020

from tabulate import tabulate

import sys
sys.path.append('c:\\Peter\\GitHub\\CoB\\')
from pipeline.distibution_helper_functions import (distribute_files)

# Set parameters
# Locations MELB, SBM, SIM, CSI (SUIBE)
location = 'SBM'
year = 2019
semester = 3

# Folder containing file based on initial parameters
source = 'H:\\Projects\\CoB\\Course_Assessment_Moderation\\{}S{}\\{}\\'.format(year, semester, location)
x = distribute_files(source, school_position=0, course_code_position=1)

print('{} files distributed\n {} files remain'.format(x[0], x[1]))


    

