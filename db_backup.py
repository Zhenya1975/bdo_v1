import shutil

def backup_bd():
  original = r'database/datab.db'
  target = r'backup/datab.db'
  shutil.copyfile(original, target)

backup_bd()  