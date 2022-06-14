import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts, Eo_candidatesDB
from initial_values.initial_values import be_data_columns_to_master_columns
from datetime import datetime
# from app import app

db = extensions.db

be_data_columns_to_master_columns = be_data_columns_to_master_columns

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

    
    

def solve_conflict(eo_code, eo_conflict_field, conflict_field_value):
  conflict_record = Eo_data_conflicts.query.filter_by(eo_code = eo_code, eo_conflict_field = eo_conflict_field, eo_conflict_status = "active").first()
  conflict_record.eo_conflict_status = "resolved"
  # добавляем запись в лог-файл
  log_data_new_record = LogsDB(log_text = f"Разрешен конфликт по полю {eo_conflict_field} в eo_code ({eo_code}). Значение поля {eo_conflict_field} в мастер-данных: {conflict_field_value}", 	log_status = "new")
  db.session.add(log_data_new_record)
  db.session.commit()

def rewrite_conflict(eo_code, eo_conflict_field, conflict_field_value_be, conflict_field_value_masterdata):
  conflict_record = Eo_data_conflicts.query.filter_by(eo_code = eo_code, eo_conflict_field = eo_conflict_field, eo_conflict_status = "active").first()
  conflict_record.eo_conflict_field_uploaded_data = conflict_field_value_be
  conflict_record.eo_conflict_field_current_master_data = conflict_field_value_masterdata
  log_data_new_record = LogsDB(log_text = f"В таблице конфликтов есть запись о конфликте по полю {eo_conflict_field} eo_code ({eo_code})", log_status = "new")
  db.session.add(log_data_new_record)
  db.session.commit()
  
def create_conflict(be_eo_data_row_no, be_data_eo_code, eo_conflict_field, eo_conflict_field_current_master_data, eo_conflict_field_uploaded_data, infodata_filename, infodata_sender_email, infodata_sender_email_date):
  
  new_conflict_record = Eo_data_conflicts(be_eo_data_row_no = be_eo_data_row_no, eo_code = be_data_eo_code, eo_conflict_field = eo_conflict_field, eo_conflict_field_current_master_data = eo_conflict_field_current_master_data, eo_conflict_field_uploaded_data = eo_conflict_field_uploaded_data, eo_conflict_description = f"EO {be_data_eo_code} в поле {eo_conflict_field} значение из файла {eo_conflict_field_uploaded_data} не соответствует значению в мастер-файле {eo_conflict_field_current_master_data}", filename = infodata_filename, sender_email = infodata_sender_email, email_date = infodata_sender_email_date)
          
  db.session.add(new_conflict_record)
  # добавляем новую запись в лог файл
  log_data_new_record = LogsDB(log_text = f"Добавлена запись о новом конфликте. В eo_code ({be_data_eo_code})в поле {eo_conflict_field} значение из файла ({eo_conflict_field_uploaded_data}) не соответствует значению в мастер-файле ({eo_conflict_field_current_master_data})", log_status = "new")
  db.session.add(log_data_new_record)
  db.session.commit()



def field_check_status(be_eo_data_row_no, be_data_eo_code, field_name, field_be_data, field_master_data, infodata_filename, infodata_sender_email, infodata_sender_email_date):
  field_status ={}
  field_status['field_name'] = field_name
  field_status['be_data'] = field_be_data
  field_status['master_data'] = field_master_data

  if field_be_data == field_master_data:
    field_status['values_status'] = 'equal'
  else:
    field_status['values_status'] = 'not_equal'

  # проверяем на наличие конфликта с текущим eo_code и eo_master_data_garno
  conflict_data = Eo_data_conflicts.query.filter_by(eo_code = be_data_eo_code, eo_conflict_field = field_name, eo_conflict_status = "active").first()

  if conflict_data:
    field_status['conflict_status'] = 'exist'
  else:
    field_status['conflict_status'] = 'not_exist'
  
# если значения равны и конфликт есть, то разрешаем конфликт
  if  field_status['values_status'] == 'equal' and  field_status['conflict_status'] == 'exist':
    solve_conflict(be_data_eo_code, field_name, field_be_data)
  
  # если значения не равны и конфликт есть, то даем перезаписываем конфликт, даем лог и идем дальше   
  elif field_status['values_status'] == 'not_equal' and  field_status['conflict_status'] == 'exist':
    rewrite_conflict(be_data_eo_code, field_name, field_be_data, field_master_data)

  # если значения не равны и конфликта нет, то создаем конфликт
  elif field_status['values_status'] == 'not_equal' and  field_status['conflict_status'] == 'not_exist': 
    create_conflict(be_eo_data_row_no, be_data_eo_code, field_name, field_master_data, field_be_data, infodata_filename, infodata_sender_email, infodata_sender_email_date)  
  
    # если значения равны и конфликта нет, то ничего не происходит  - идем дальше
  elif field_status['values_status'] == 'equal' and  field_status['conflict_status'] == 'not_exist':
    pass

  else:
    print("что-то непонятное")



def read_be_eo_xlsx():
  # with app.app_context():
  # читаем excel с данными из бизнес-единиц. Проверяем - если нет нужного листа с данными, то отдаем ошибку
  be_eo_data = pd.DataFrame()
  try:
    be_eo_raw_data = pd.read_excel('uploads/be_eo_data.xlsx', sheet_name='be_eo_data', index_col = False)
 
    be_eo_data = be_eo_raw_data.rename(columns=be_data_columns_to_master_columns)
    # поля с датами - в формат даты
    be_eo_data['gar_no'].fillna(0, inplace = True)
    be_eo_data["gar_no"] = be_eo_data["gar_no"].astype(str)
    be_eo_data["eo_code"] = be_eo_data["eo_code"].astype(str)
    # print(be_eo_data.info())
  except Exception as e:
    print("не удалось прочитать файл uploads/be_eo_data.xlsx. Ошибка: ", e)
    log_data_new_record = LogsDB(log_text = f"не удалось прочитать файл uploads/be_eo_data.xlsx. Ошибка: , {e})", log_status = "new")
    db.session.add(log_data_new_record)

  # читаем данные из инфо вкладки   
  be_data_info = pd.DataFrame()
  try:
    be_data_info = pd.read_excel('uploads/be_eo_data.xlsx', sheet_name='be_eo_file_data', index_col = False, dtype=str)
  except Exception as e:
    print("не удалось прочитать данные из инфо-вкладки файла uploads/be_eo_data.xlsx. Ошибка: ", e)
    log_data_new_record = LogsDB(log_text = f"не удалось прочитать данные из инфо-вкладки файла uploads/be_eo_data.xlsx. Ошибка: , {e})", log_status = "new")
    db.session.add(log_data_new_record)
    
  infodata_filename = be_data_info.loc[be_data_info.index[0], ['filename']][0]
  infodata_sender_email = be_data_info.loc[be_data_info.index[0], ['sender_email']][0]
  infodata_sender_email_date = be_data_info.loc[be_data_info.index[0], ['e-mail_date']][0]

   
  # предыдущие данные в лог файле ресетим
  log_data_updated = LogsDB.query.update(dict(log_status='old'))
  db.session.commit()


  ################################################ чтение загруженного файла ###############################################
  for row in be_eo_data.itertuples():
    be_eo_data_row_no = getattr(row, "be_eo_data_row_no")
    be_data_eo_code = getattr(row, "eo_code")
    be_data_gar_no = str(getattr(row, "gar_no"))
    be_data_operation_start_date_raw = getattr(row, "operation_start_date")
    be_data_expected_operation_finish_date_raw = getattr(row, "expected_operation_finish_date")
    be_data_expected_operation_finish_date = read_date(be_data_expected_operation_finish_date_raw)

    
    # читаем мастер-файл из базы
    eo_master_data=Eo_DB.query.filter_by(eo_code=be_data_eo_code).first()
    be_data_operation_start_datetime = read_date(be_data_operation_start_date_raw)
    
    if eo_master_data == None:
      new_eo_candidate_record = Eo_candidatesDB(eo_code=be_data_eo_code, gar_no = be_data_gar_no, operation_start_date = be_data_operation_start_datetime)
      db.session.add(new_eo_candidate_record)
      log_data_new_record = LogsDB(log_text = f"Добавлен кандидат на добавление в мастер. eo_code: {be_data_eo_code}, gar_no: {be_data_gar_no}", log_status = "new")
      db.session.add(log_data_new_record)
      
    # если в мастер-данных есть запись с текущим eo_code, то последовательно проверяем значения в полях
    else:
      ############# ПОЛЕ ГАРАЖНЫЙ НОМЕР gar_no ##############################
      eo_master_data_garno = eo_master_data.gar_no
      # print("be_data_gar_no: ", be_data_gar_no, type(be_data_gar_no))
      # print("eo_master_data_garno: ", eo_master_data_garno, type(eo_master_data_garno))
      field_name = "gar_no"
      field_be_data = be_data_gar_no
      field_master_data = eo_master_data_garno

      # запуск функции по проверке статуса текущего поля
      field_check_status(
        be_eo_data_row_no,
        be_data_eo_code,
        field_name, 
        field_be_data,
        field_master_data,
        infodata_filename, 
        infodata_sender_email, 
        infodata_sender_email_date
      )

      ############# ПОЛЕ Плановая дата вывода из эксплуат expected_operation_finish_date ##############################
      eo_master_data_expected_operation_finish_datetime = eo_master_data.expected_operation_finish_date
      field_master_data = eo_master_data_expected_operation_finish_datetime.date()
      field_name = 'expected_operation_finish_datetime'
      be_data_expected_operation_finish_datetime = be_data_expected_operation_finish_date.date()
      field_be_data = str(be_data_expected_operation_finish_datetime)

      field_check_status(
        be_eo_data_row_no,
        be_data_eo_code,
        field_name, 
        field_be_data,
        field_master_data,
        infodata_filename, 
        infodata_sender_email, 
        infodata_sender_email_date
      )
      
      
      ############# ПОЛЕ Дата начала эксплуатации operation_start_date ##############################
      eo_master_data_operation_start_datetime = eo_master_data.operation_start_date
      eo_master_data_operation_start_date = eo_master_data_operation_start_datetime.date()
      field_name = "operation_start_date"
      
      

      if be_data_operation_start_datetime == datetime.strptime('1.1.2199', '%d.%m.%Y'):
        be_data_operation_start_datetime = eo_master_data_operation_start_datetime
          
      be_data_operation_start_date = be_data_operation_start_datetime.date()
      
      field_be_data = str(be_data_operation_start_date)
      field_master_data = str(eo_master_data_operation_start_date)
      # print("eo_master_data_operation_start_date", eo_master_data_operation_start_date)

      field_check_status(
        be_eo_data_row_no,
        be_data_eo_code,
        field_name, 
        field_be_data,
        field_master_data,
        infodata_filename, 
        infodata_sender_email, 
        infodata_sender_email_date
      )
      
 