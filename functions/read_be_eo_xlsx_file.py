import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts, Eo_candidatesDB
from initial_values.initial_values import be_data_columns_to_master_columns
from datetime import datetime
# from app import app

db = extensions.db

be_data_columns_to_master_columns = be_data_columns_to_master_columns

def solve_conflict(eo_code, eo_conflict_field, conflict_field_value):
  conflict_record = Eo_data_conflicts.query.filter_by(eo_code = eo_code, eo_conflict_field = eo_conflict_field).first()
  conflict_record.eo_conflict_status = "resolved"
  # добавляем запись в лог-файл
  log_data_new_record = LogsDB(log_text = f"Разрешен конфликт с гаражным номером в eo_code ({eo_code}). Значение гаражного номера в мастер-данных: {conflict_field_value}", 	log_status = "new")
  db.session.add(log_data_new_record)
  db.session.commit()

def read_be_eo_xlsx():
  # with app.app_context():
  # читаем excel с данными из бизнес-единиц. Проверяем - если нет нужного листа с данными, то отдаем ошибку
  be_eo_data = pd.DataFrame()
  try:
    be_eo_raw_data = pd.read_excel('uploads/be_eo_data.xlsx', sheet_name='be_eo_data', index_col = False, dtype=str)
 
    be_eo_data = be_eo_raw_data.rename(columns=be_data_columns_to_master_columns)
    # поля с датами - в формат даты
    be_eo_data['gar_no'].fillna(0, inplace = True)
    be_eo_data["gar_no"] = be_eo_data["gar_no"].astype(str)
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
    # получаем eo_code
    be_eo_data_row_no = getattr(row, "be_eo_data_row_no")
    be_data_eo_code = getattr(row, "eo_code")
    be_data_gar_no = str(getattr(row, "gar_no"))
    be_data_operation_start_date_raw = getattr(row, "operation_start_date")
    # конвертируем в datetime
    try:
      be_data_operation_start_date = datetime.strptime(be_data_operation_start_date_raw, '%d.%m.%Y')
      be_data_operation_start_date = be_data_operation_start_date.date()
    except:
      print("не удалось конвертировать текст из файла БЕ в дату")
      ######### здесь надо создавать конфликт
    
    # читаем мастер-файл из базы
    eo_master_data=Eo_DB.query.filter_by(eo_code=be_data_eo_code).first()
    # operation_start_date в мастер данных -> в формат даты
    master_data_operation_start_date = eo_master_data.operation_start_date.date()

    

    # если в мастер-данных нет записи с текущим eo_code, то добавляем запись в таблицу кандидатов на добавление
    if eo_master_data == None:
      new_eo_candidate_record = Eo_candidatesDB(eo_code=be_data_eo_code, gar_no = be_data_gar_no)
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
      field_status ={}
      field_status['field_name'] = "gar_no"
      field_status['be_data'] = be_data_gar_no
      field_status['master_data'] = eo_master_data_garno

      if be_data_gar_no == eo_master_data_garno:
        field_status['values_status'] = 'equal'
      else:
        field_status['values_status'] = 'not_equal'

      # проверяем на наличие конфликта с текущим eo_code и eo_master_data_garno
      conflict_data = Eo_data_conflicts.query.filter_by(eo_code = be_data_eo_code, eo_conflict_field = "gar_no", eo_conflict_field_current_master_data = eo_master_data_garno).first()
      if conflict_data:
        field_status['conflict_status'] = 'exist'
      else:
        field_status['conflict_status'] = 'not_exist'
      
      # если значения равны и конфликт есть, то разрешаем конфликт
      if  field_status['values_status'] == 'equal' and  field_status['conflict_status'] == 'exist':
        solve_conflict(be_data_eo_code, field_status['field_name'], field_status['be_data'])
        
      
        
      # # ...... то проверяем на наличие конфликта
      # # Если гаражные номера не совпадают, то это новый конфликт
      # if eo_master_data_garno != be_data_gar_no:
      #   # проверяем есть ли уже созданная ранее запись об этом конфликте
      #   potencial_conflict_record = Eo_data_conflicts.query.filter_by(eo_code = be_data_eo_code, eo_conflict_field = "gar_no", eo_conflict_field_current_master_data = eo_master_data_garno, eo_conflict_field_uploaded_data = be_data_gar_no).first()
        
      #   # проверяем есть ли запись о конфликте
      #   if potencial_conflict_record:
      #     # если запись о конфликте есть, то просто выводим 
      #     log_data_new_record = LogsDB(log_text = f"В таблице конфликтов уже есть запись о конфликте по полю 'гаражный номер' eo_code ({be_data_eo_code})", log_status = "new")
      #     db.session.add(log_data_new_record)
      #   else:  
      #     # если записи о конфликте нет, то создаем новую запись о конфликте
      #     new_conflict_record = Eo_data_conflicts(be_eo_data_row_no = be_eo_data_row_no, eo_code = be_data_eo_code, eo_conflict_field = "gar_no", eo_conflict_field_current_master_data = eo_master_data_garno, eo_conflict_field_uploaded_data = be_data_gar_no, eo_conflict_description = f"В EO {be_data_eo_code} гаражный номер в файле из бизнес-единицы {be_data_gar_no} не соответствует гаражному номеру в мастер-файле {eo_master_data_garno}", filename = infodata_filename, sender_email = infodata_sender_email, email_date = infodata_sender_email_date)
  
          
      #     db.session.add(new_conflict_record)
      #     # добавляем новую запись в лог файл
      #     log_data_new_record = LogsDB(log_text = f"Добавлена запись о новом конфликте. В eo_code ({be_data_eo_code}) гаражный номер в загруженном файле ({be_data_gar_no}) не соответствует гаражному номеру в мастер-файле ({eo_master_data_garno})", log_status = "new")
      #     db.session.add(log_data_new_record)
      #     print("Создан новый конфликт. eo_code: ", be_data_eo_code, ". Гаражный номер в мастер-файле: ", eo_master_data_garno, ", гаражный номер в загружаемом файле: ", be_data_gar_no)
      # # если гаражные номера совпадают, то конфликта нет и движемся дальше
      #   db.session.commit()
      
      # # гаражные номера равны
      # else:
        
      #   # проверяем есть ли конфликт
      #   potencial_conflict_record = Eo_data_conflicts.query.filter_by(eo_code = be_data_eo_code, eo_conflict_field = "gar_no", eo_conflict_field_current_master_data = eo_master_data_garno).first()
      #   # проверяем есть ли запись о конфликте
      #   if potencial_conflict_record:
      #     potencial_conflict_record.eo_conflict_status = "resolved"
      #   # добавляем запись в лог-файл
      #     log_data_new_record = LogsDB(log_text = f"Разрешен конфликт с гаражным номером в eo_code ({be_data_eo_code}). Значение гаражного номера в мастер-данных: {be_data_gar_no}", 	log_status = "new")
      #     db.session.add(log_data_new_record)
      #     db.session.commit()
        
        
    # db.session.commit()  
        
      
    



  

  

  
  
  