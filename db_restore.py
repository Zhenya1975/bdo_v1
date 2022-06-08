import shutil

def restore_bd():
  original = r'backup/datab.db'
  target = r'database/datab.db'
  shutil.copyfile(original, target)

restore_bd()