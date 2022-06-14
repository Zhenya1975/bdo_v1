import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts, Eo_candidatesDB
from initial_values.initial_values import sap_columns_to_master_columns
from datetime import datetime
# from app import app

db = extensions.db

sap_columns_to_master_columns = sap_columns_to_master_columns

def read_date(date_input):  
  if "timestamp" in str(type(date_input)):
    date_output = date_input
    return date_output
  elif "str" in str(type(date_input)):
    try:
      date_output = datetime.strptime(date_input, '%d.%m.%Y')
      return date_output
    except Exception as e:
      print(f"не удалось сохранить в дату '{date_input}'. Ошибка: ", e)
  elif "nat" in str(type(date_input)) or "NaT" in str(type(date_input)):
    date_output = datetime.strptime('1.1.2199', '%d.%m.%Y')
    return date_output
  else:
    print("не покрыто типами данных дат", type(date_input), date_input)


def read_sap_eo_xlsx():
  # with app.app_context():
  sap_eo_raw_data = pd.read_excel('uploads/sap_eo_data.xlsx', index_col = False, dtype=str)
  
  sap_eo_data = sap_eo_raw_data.rename(columns=sap_columns_to_master_columns)
  date_time_plug = '31/12/2199 23:59:59'
  date_time_plug = datetime.strptime(date_time_plug, '%d/%m/%Y %H:%M:%S')

  
  try:
    sap_eo_data["operation_start_date"] = pd.to_datetime(sap_eo_data["operation_start_date"])
    sap_eo_data['operation_start_date'].fillna(date_time_plug, inplace = True)
  except:
    sap_eo_data["operation_start_date"] = date_time_plug

  try:
    sap_eo_data['gar_no'].fillna(0, inplace = True)
  except:
    sap_eo_data['gar_no'] = "plug"
  
  sap_eo_data["gar_no"] = sap_eo_data["gar_no"].astype(str)


  try:  
    sap_eo_data["expected_operation_finish_date"] = pd.to_datetime(sap_eo_data["expected_operation_finish_date"])
    sap_eo_data['expected_operation_finish_date'].fillna(date_time_plug, inplace = True)
  except:
    sap_eo_data["expected_operation_finish_date"] = date_time_plug
    
  # предыдущие данные в лог файле ресетим
  log_data_updated = LogsDB.query.update(dict(log_status='old'))
  db.session.commit()

  # итерируемся по полученному файлу
  for row in sap_eo_data.itertuples():
    eo_code_excel = getattr(row, "eo_code")
    
    be_code_excel = 0
    try:
      be_code_excel = getattr(row, "be_code")
    except:
      pass
    
    eo_description_excel = "plug"
    try:
      eo_description_excel = getattr(row, "eo_description")
    except:
      pass
    
    teh_mesto_excel = "plug"
    try:
      teh_mesto_excel = getattr(row, "teh_mesto")
    except:
      pass
    
    gar_no_excel = "plug"  
    try:
      gar_no_excel = str(getattr(row, "gar_no"))
    except:
      pass

    head_type_excel = "plug"
    try:
      head_type_excel = str(getattr(row, "head_type"))
    except:
      pass  

    eo_model_id_excel = 0
    try:
      eo_model_id_excel = getattr(row, "eo_model_id")
    except:
      pass   

    
    operation_start_date_raw = getattr(row, "operation_start_date")
    operation_start_date = read_date(operation_start_date_raw)

    try:
      expected_operation_finish_date_raw = getattr(row, "expected_operation_finish_date")
      expected_operation_finish_date = read_date(expected_operation_finish_date_raw)
    except:
      pass
    # читаем мастер-файл из базы
    eo_master_data=Eo_DB.query.filter_by(eo_code=eo_code_excel).first()
    # если данных нет, то добавляем запись.
    if eo_master_data == None:
      print(eo_code_excel, " - новый eo")
      new_eo_master_data_record = Eo_DB(be_code=be_code_excel, eo_code=eo_code_excel, eo_description=eo_description_excel, teh_mesto=teh_mesto_excel, gar_no=gar_no_excel, head_type = head_type_excel, eo_model_id = eo_model_id_excel, operation_start_date=operation_start_date, expected_operation_finish_date = expected_operation_finish_date)
      
      db.session.add(new_eo_master_data_record)
      # добавляем новую запись в лог файл
      log_data_new_record = LogsDB(log_text = f"В eo_master_data добавлена запись eo: {eo_code_excel}", log_status = "new")
      db.session.add(log_data_new_record)
      db.session.commit()
   
    # иначе обновляем данные в мастер-файле
    else:
      print(eo_code_excel, " - существующий eo")
      if be_code_excel != 0:
        eo_master_data.be_code = be_code_excel
      
      if eo_description_excel != "plug":
        eo_master_data.eo_description = eo_description_excel

      if teh_mesto_excel != "plug":
        eo_master_data.teh_mesto = teh_mesto_excel
      
      if gar_no_excel != "plug":
        eo_master_data.gar_no = gar_no_excel
      
      # eo_master_data.eo_description = eo_description
      
      
      if head_type_excel != "plug":
        eo_master_data.head_type = head_type_excel
      
      if eo_model_id_excel != "plug":
        eo_master_data.eo_model_id = eo_model_id_excel

      eo_master_data.operation_start_date = operation_start_date
      
      eo_master_data.expected_operation_finish_date = expected_operation_finish_date
      print("100000065632 expected_operation_finish_date", expected_operation_finish_date, type(expected_operation_finish_date))
      db.session.commit()
    
    db.session.commit()

    # сверяемся с файлом кандидатов на добавление.
    add_candidate_record  = Eo_candidatesDB.query.filter_by(eo_code = eo_code_excel).first()
    if add_candidate_record:
      # удаляем запись из таблицы add_candidate_record
      db.session.delete(add_candidate_record)
      log_data_new_record = LogsDB(log_text = f"Добавлена запись из списка кандидатов на добавление. eo_code: {eo_code}", 	log_status = "new")
      db.session.add(log_data_new_record)
      db.session.commit()

    
    # сверяемся с файлом конфликтов.
    # по полю "Гаражный номер"
    # ищем запись в таблице конфликтов
    potencial_gar_no_conflict = Eo_data_conflicts.query.filter_by(eo_code = eo_code_excel, eo_conflict_field = "gar_no").first()
    # если запись находим
    if potencial_gar_no_conflict:
      # обновляем запись в поле eo_conflict_field_current_master_data
      potencial_gar_no_conflict.eo_conflict_field_current_master_data = str(gar_no_excel)
      db.session.commit()
      # проверяем на ситуацию в конфликте после внесения изменений
      if str(potencial_gar_no_conflict.eo_conflict_field_current_master_data) == (potencial_gar_no_conflict.eo_conflict_field_uploaded_data):
        potencial_gar_no_conflict.eo_conflict_status = "resolved"
        log_data_new_record = LogsDB(log_text = f"Разрешен конфликт с гаражным номером в eo_code ({eo_code_excel}). Текущее значение гаражного номера в мастер-данных: {gar_no_excel}", 	log_status = "new")
        db.session.add(log_data_new_record)
        
        db.session.commit()
 
      

