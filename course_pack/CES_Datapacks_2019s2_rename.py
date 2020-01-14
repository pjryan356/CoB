import os


# Directory containing files
directory = 'H:\\Projects\\CoB\\CES\\Courses\\2019S2\\VBE\\'

for filename in os.listdir(directory):
    if filename.endswith("S1.pdf"):
      print(os.path.join(directory, filename))
      os.rename(os.path.join(directory, filename), os.path.join(directory, filename[:-6]+'S2.pdf'))
      continue
    else:
      continue