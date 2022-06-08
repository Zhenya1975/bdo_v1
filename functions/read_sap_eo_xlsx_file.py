import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts, Eo_candidatesDB
from initial_values.initial_values import sap_columns_to_master_columns
from datetime import datetime
# from app import app

db = extensions.db

sap_columns_to_master_columns = sap_columns_to_master_columns

def read_sap_eo_xlsx():
  # with app.app_context():
  sap_eo_raw_data = pd.read_excel('uploads/sap_eo_data.xlsx', index_col = False, dtype=str)
  
  sap_eo_data = sap_eo_raw_data.rename(columns=sap_columns_to_master_columns)
  # поля с датами - в формат даты
  sap_eo_data["operation_start_date"] = pd.to_datetime(sap_eo_data["operation_start_date"])
  sap_eo_data['gar_no'].fillna(0, inplace = True)
  sap_eo_data["gar_no"] = sap_eo_data["gar_no"].astype(str)
   
  date_time_plug = '31/12/2199 23:59:59'
  date_time_plug = datetime.strptime(date_time_plug, '%d/%m/%Y %H:%M:%S')
  sap_eo_data['operation_start_date'].fillna(date_time_plug, inplace = True)

  # предыдущие данные в лог файле ресетим
  log_data_updated = LogsDB.query.update(dict(log_status='old'))
  db.session.commit()
  # print(sap_eo_data.info())
  # итерируемся по полученному файлу
  for row in sap_eo_data.itertuples():
    # получаем eo_code
    be_code = getattr(row, "be_code")
    eo_code = getattr(row, "eo_code")
    eo_description = getattr(row, "eo_description")
    teh_mesto = getattr(row, "teh_mesto")
    gar_no = str(getattr(row, "gar_no"))
    operation_start_date = getattr(row, "operation_start_date")

    
    # читаем мастер-файл из базы
    eo_master_data=Eo_DB.query.filter_by(eo_code=eo_code).first()
    # если данных нет, то добавляем запись.
    if eo_master_data == None:
      # new_eo_master_data_record = Eo_DB(be_code=be_code, eo_code=eo_code, eo_description=eo_description, teh_mesto=teh_mesto, gar_no=gar_no)
      new_eo_master_data_record = Eo_DB(be_code=be_code, eo_code=eo_code, eo_description=eo_description, teh_mesto=teh_mesto, gar_no=gar_no, operation_start_date=operation_start_date)
      db.session.add(new_eo_master_data_record)
      # добавляем новую запись в лог файл
      log_data_new_record = LogsDB(log_text = f"В eo_master_data добавлена запись eo: {eo_code}", log_status = "new")
      db.session.add(log_data_new_record)
    # иначе обновляем данные в мастер-файле
    else:
      eo_master_data.eo_description = eo_description
      eo_master_data.teh_mesto = teh_mesto
      eo_master_data.gar_no = gar_no
    db.session.commit()

    # сверяемся с файлом кандидатов на добавление.
    add_candidate_record  = Eo_candidatesDB.query.filter_by(eo_code = eo_code).first()
    if add_candidate_record:
      # удаляем запись из таблицы add_candidate_record
      db.session.delete(add_candidate_record)
      log_data_new_record = LogsDB(log_text = f"Добавлена запись из списка кандидатов на добавление. eo_code: {eo_code}", 	log_status = "new")
      db.session.add(log_data_new_record)
      db.session.commit()

    
    # сверяемся с файлом конфликтов.
    # по полю "Гаражный номер"
    # ищем запись в таблице конфликтов
    potencial_gar_no_conflict = Eo_data_conflicts.query.filter_by(eo_code = eo_code, eo_conflict_field = "gar_no").first()
    # если запись находим
    if potencial_gar_no_conflict:
      # обновляем запись в поле eo_conflict_field_current_master_data
      potencial_gar_no_conflict.eo_conflict_field_current_master_data = str(gar_no)
      db.session.commit()
      # проверяем на ситуацию в конфликте после внесения изменений
      if str(potencial_gar_no_conflict.eo_conflict_field_current_master_data) == (potencial_gar_no_conflict.eo_conflict_field_uploaded_data):
        potencial_gar_no_conflict.eo_conflict_status = "resolved"
        log_data_new_record = LogsDB(log_text = f"Разрешен конфликт с гаражным номером в eo_code ({eo_code}). Текущее значение гаражного номера в мастер-данных: {gar_no}", 	log_status = "new")
        db.session.add(log_data_new_record)
        
        db.session.commit()
 
      

        
      
        




    #   # смотрим в таблицу конфликтов и ищем запись с конфликтом 
    #   
      
    #   # если запись о конфликте есть и если значения в конфликтующих полях равны, то разрешаем этот конфликт
    #   if potencial_gar_no_conflict and current_master_data_garno == uploaded_garno_value:
    #     potencial_gar_no_conflict.eo_conflict_status = "resolved"
    #     # и пишем в лог запись о разрешении конфликта
    #     resolved_gar_no = potencial_gar_no_conflict.eo_conflict_field_current_master_data
    #     log_data_new_record = LogsDB(log_text = f"Разрешен конфликт несоответствия гаражного номера ({resolved_gar_no}) ")
    #     db.session.add(log_data_new_record)
    #     # и обновляем запись в мастер-данных
    #     eo_master_data.gar_no = uploaded_garno_value
      
    #   # если записи об активных конфликтах нет, то проверяем вдруг возник новый конфликт
    #   # для этого сравниваем значение из мастер-данных и загруженного файла
    #   # если значения отличаются
    #   elif current_master_data_garno != gar_no:
    #     # проверяем есть ли уже эта запись в таблице конфликтов
    #     # для проверки сравниваем стринг со стрингом
    #     current_master_data_gar_no = str(eo_master_data.gar_no)
    #     uploaded_gar_no_value = str(gar_no)
        
    #     # ищем запись с этими данными в таблице конфликтов
        
    #     potencial_gar_no_conflict = Eo_data_conflicts.query.filter_by(eo_conflict_field = "gar_no", eo_conflict_field_current_master_data=str(current_master_data_garno), eo_conflict_status="active").first()
        
    #     # если записи нет, то создаем новую запись в конфликтах
    #     if potencial_gar_no_conflict == None:
    #       new_conflict_record = Eo_data_conflicts(eo_code = eo_code, eo_conflict_field = 'gar_no', eo_conflict_description=f"Гаражный номер в загруженном файле ({gar_no}) не соответствует гаражному номеру в мастер-файле ({eo_master_data.gar_no})", eo_conflict_field_current_master_data = str(current_master_data_gar_no), eo_conflict_field_uploaded_data=str(uploaded_gar_no_value))
    #       db.session.add(new_conflict_record)

    #       # добавляем новую запись в лог файл
    #       log_data_new_record = LogsDB(log_text = f"Гаражный номер в загруженном файле ({gar_no}) не соответствует гаражному номеру в мастер-файле ({eo_master_data.gar_no}). Запись в мастер-файл не добавлена. Информация о конфликте - в списке конфликтов", log_status = "new")
    #       db.session.add(log_data_new_record)
        
    #     # если запись о конфликте нашлась, то пишем в лог, но не добавляем запись в конфликты
    #     else:
    #       # добавляем новую запись в лог файл
    #       log_data_new_record = LogsDB(log_text = f"В лог-файле уже есть запись о конфликте. Гаражный номер в загруженном файле ({gar_no}) не соответствует гаражному номеру в мастер-файле ({eo_master_data.gar_no})", log_status = "new")
    #       db.session.add(log_data_new_record)

    #   else:
    #     print(f"в записи с гаражным номером {current_master_data_garno} конфликтов нет")
      
    #   eo_master_data.operation_start_date=operation_start_date

    #   db.session.commit()
    
        
    



  # переименовываем колонки из sap наименований в master
  



