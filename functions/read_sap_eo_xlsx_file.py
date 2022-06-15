import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts, Eo_candidatesDB
from initial_values.initial_values import sap_columns_to_master_columns
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta


# from app import app

db = extensions.db

sap_columns_to_master_columns = sap_columns_to_master_columns

def calculate_operation_finish_date(operation_start_date_raw, operation_period_years_raw, eo_code):
  if "timestamp" in str(type(operation_start_date_raw)) or 'datetime' in str(type(operation_start_date_raw)):
    operation_start_date = operation_start_date_raw
  elif "str" in str(type(operation_start_date_raw)):
    try:
      operation_start_date = datetime.strptime(operation_start_date_raw, '%d.%m.%Y')
    except:
      pass
    try:
      operation_start_date = datetime.strptime(operation_start_date_raw, '%Y-%m-%d %H:%M:%S')
    except:
      pass  
    try:
      operation_start_date = datetime.strptime(operation_start_date_raw, '%Y-%m-%d')
    except Exception as e:
      print(f"eo_code: {eo_code}. Не удалось сохранить в дату '{operation_start_date_raw}, тип: {type(operation_start_date_raw)}'. Ошибка: ", e)
  
  try:
    operation_period_years = int(operation_period_years_raw)  
  except Exception as e:
    print(f"eo_code: {eo_code}. Не удалось получить период эксплуатации '{operation_period_years_raw}, тип: {type(operation_period_years_raw)}'. Ошибка: ", e)
    operation_period_years = 1313
  calculate_operation_finish_date = operation_start_date + relativedelta(years=operation_period_years)
  return calculate_operation_finish_date

def read_date(date_input, eo_code):  
  if "timestamp" in str(type(date_input)):
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
  elif "nat" in str(type(date_input)) or "NaT" in str(type(date_input)):
    date_output = datetime.strptime('1.1.2199', '%d.%m.%Y')
    return date_output
  else:
    print("не покрыто типами данных дат", type(date_input), date_input)


def read_sap_eo_xlsx():
  # with app.app_context():
  sap_eo_raw_data = pd.read_excel('uploads/sap_eo_data.xlsx', index_col = False, dtype=str)
  
  sap_eo_data = sap_eo_raw_data.rename(columns=sap_columns_to_master_columns)
  sap_eo_column_list = list(sap_eo_data.columns)
    
  # предыдущие данные в лог файле ресетим
  log_data_updated = LogsDB.query.update(dict(log_status='old'))
  db.session.commit()

  # итерируемся по полученному файлу
  for row in sap_eo_data.itertuples():
    eo_code_excel = getattr(row, "eo_code")
  
    # читаем мастер-файл из базы
    eo_master_data=Eo_DB.query.filter_by(eo_code=eo_code_excel).first()
    # если данных нет, то добавляем запись.
    if eo_master_data == None:
      new_eo_master_data_record = Eo_DB(eo_code=eo_code_excel)
      db.session.add(new_eo_master_data_record)
      # добавляем новую запись в лог файл
      log_data_new_record = LogsDB(log_text = f"В eo_master_data добавлена запись eo: {eo_code_excel}", log_status = "new")
      db.session.add(log_data_new_record)
      db.session.commit()
   
    # иначе обновляем данные в мастер-файле
    else:
      if 'be_code' in sap_eo_column_list:
        eo_master_data.be_code = getattr(row, "be_code")

      if 'eo_description' in sap_eo_column_list:
        eo_master_data.eo_description = getattr(row, "eo_description")

      if 'teh_mesto' in sap_eo_column_list:
        eo_master_data.teh_mesto = getattr(row, "teh_mesto")

      if 'gar_no' in sap_eo_column_list:
        eo_master_data.gar_no = getattr(row, "gar_no")
      
      if 'head_type' in sap_eo_column_list:
        eo_master_data.head_type = getattr(row, "head_type")  

      if 'eo_model_id' in sap_eo_column_list:
        eo_master_data.eo_model_id = getattr(row, "eo_model_id")
      
      operation_start_date = eo_master_data.operation_start_date
      if 'operation_start_date' in sap_eo_column_list:
        operation_start_date_raw = getattr(row, "operation_start_date")
        operation_start_date = read_date(operation_start_date_raw, eo_code_excel)
        eo_master_data.operation_start_date = operation_start_date

      if 'expected_operation_period_years' in sap_eo_column_list:
        eo_master_data.expected_operation_period_years = getattr(row, "expected_operation_period_years")
        # пишем расчетное значение даты завершения эксплуатации
        calculated_operation_finish_date = calculate_operation_finish_date(operation_start_date, getattr(row, "expected_operation_period_years"), eo_code_excel)
        eo_master_data.expected_operation_finish_date = calculated_operation_finish_date

      if 'expected_operation_finish_date' in sap_eo_column_list:
        expected_operation_finish_date_raw = getattr(row, "expected_operation_finish_date")
        expected_operation_finish_date = read_date(expected_operation_finish_date_raw, eo_code_excel)
        eo_master_data.expected_operation_finish_date = expected_operation_finish_date
      
      db.session.commit()
    
    db.session.commit()

    # сверяемся с файлом кандидатов на добавление.
    add_candidate_record  = Eo_candidatesDB.query.filter_by(eo_code = eo_code_excel).first()
    if add_candidate_record:
      # удаляем запись из таблицы add_candidate_record
      db.session.delete(add_candidate_record)
      log_data_new_record = LogsDB(log_text = f"Добавлена запись из списка кандидатов на добавление. eo_code: {eo_code_excel}", 	log_status = "new")
      db.session.add(log_data_new_record)
      db.session.commit()

    
    # сверяемся с файлом конфликтов.
    # по полю "Гаражный номер"
    # ищем запись в таблице конфликтов
    potencial_gar_no_conflict = Eo_data_conflicts.query.filter_by(eo_code = eo_code_excel, eo_conflict_field = "gar_no").first()
    # если запись находим
    if potencial_gar_no_conflict:
      # обновляем запись в поле eo_conflict_field_current_master_data
      potencial_gar_no_conflict.eo_conflict_field_current_master_data = str(getattr(row, "gar_no"))
      db.session.commit()
      # проверяем на ситуацию в конфликте после внесения изменений
      if str(potencial_gar_no_conflict.eo_conflict_field_current_master_data) == (potencial_gar_no_conflict.eo_conflict_field_uploaded_data):
        potencial_gar_no_conflict.eo_conflict_status = "resolved"
        log_data_new_record = LogsDB(log_text = f"Разрешен конфликт с гаражным номером в eo_code ({eo_code_excel}). Текущее значение гаражного номера в мастер-данных: {eo_master_data.gar_no}", 	log_status = "new")
        db.session.add(log_data_new_record)
        
        db.session.commit()
 
      

