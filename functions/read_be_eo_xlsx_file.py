import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts
from initial_values.initial_values import be_data_columns_to_master_columns
from datetime import datetime
# from app import app

db = extensions.db

be_data_columns_to_master_columns = be_data_columns_to_master_columns

def read_be_eo_xlsx():
  # with app.app_context():
  try:
    be_eo_raw_data = pd.read_excel('uploads/be_eo_data.xlsx', sheet_name='be_eo_data', index_col = False, dtype=str)
    be_eo_data = be_eo_raw_data.rename(columns=be_data_columns_to_master_columns)
    # поля с датами - в формат даты
    be_eo_data['gar_no'].fillna(0, inplace = True)
    be_eo_data["gar_no"] = be_eo_data["gar_no"].astype(str)
    print(be_eo_data.info())
  except Exception as e:
    print("не удалось прочитать файл uploads/be_eo_data.xlsx. Ошибка: ", e)
    return "fail"

  

  
  
  