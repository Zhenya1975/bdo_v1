import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts, Eo_candidatesDB
from initial_values.initial_values import be_data_columns_to_master_columns
from datetime import datetime
# from app import app


db = extensions.db

be_data_columns_to_master_columns = be_data_columns_to_master_columns


def read_date(date_input, eo_code):  
  # print(type(date_input), eo_code)
  if "timestamp" in str(type(date_input)) or 'datetime' in str(type(date_input)):
    date_output = date_input
    return date_output
  elif "str" in str(type(date_input)):
    try:
      date_output = datetime.strptime(date_input, '%d.%m.%Y')
      return date_output
    except:
      pass
    try:
      date_output = datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S')
      return date_output
    except:
      pass  
    try:
      date_output = datetime.strptime(date_input, '%Y-%m-%d')
      return date_output
    except Exception as e:
      print(f"eo_code: {eo_code}. Не удалось сохранить в дату '{date_input}, тип: {type(date_input)}'. Ошибка: ", e)
      date_output = datetime.strptime('1.1.2199', '%d.%m.%Y')
      return date_output
  
  elif "nat" in str(type(date_input)) or "NaT" in str(type(date_input)) or "float" in str(type(date_input)):
    date_output = datetime.strptime('1.1.2199', '%d.%m.%Y')
    return date_output
  else:
    print(eo_code, "не покрыто типами данных дат", type(date_input), date_input)
    date_output = datetime.strptime('1.1.2199', '%d.%m.%Y')
    return date_output

def read_update_eo_data_xlsx():
  # with app.app_context():
  # читаем excel с данными из бизнес-единиц. Проверяем - если нет нужного листа с данными, то отдаем ошибку
  update_eo_data = pd.DataFrame()
  try:
    update_eo_data_df = pd.read_excel('uploads/update_eo_data.xlsx', index_col = False)
    update_eo_column_list = list(update_eo_data_df.columns)

  except Exception as e:
    print("не удалось прочитать файл uploads/update_eo_data.xlsx. Ошибка: ", e)
    log_data_new_record = LogsDB(log_text = f"не удалось прочитать файл uploads/update_eo_data.xlsx. Ошибка: , {e})", log_status = "new")
    db.session.add(log_data_new_record)
  
    ################################################ чтение загруженного файла ###############################################
  i=0
  lenght = len(update_eo_data)
  print(update_eo_data_df)
  for row in update_eo_data_df.itertuples():
    eo_code = str(getattr(row, 'eo_code'))
    # проверяем, что запись есть
    eo_master_data=Eo_DB.query.filter_by(eo_code=eo_code).first()
    print(eo_master_data)
    if eo_master_data:
      print("запись есть")
    else:
      print("записи нет")
  