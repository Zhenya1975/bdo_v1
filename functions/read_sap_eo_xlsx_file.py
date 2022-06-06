import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts
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
  sap_eo_data["gar_no"] = sap_eo_data["gar_no"].astype(int)
  sap_eo_data['gar_no'].fillna(0, inplace = True) 
    
  date_time_plug = '31/12/2199 23:59:59'
  date_time_plug = datetime.strptime(date_time_plug, '%d/%m/%Y %H:%M:%S')
  sap_eo_data['operation_start_date'].fillna(date_time_plug, inplace = True)
  print(sap_eo_data.info())
  # итерируемся по полученному файлу
  for row in sap_eo_data.itertuples():
    # получаем eo_code
    be_code = getattr(row, "be_code")
    eo_code = getattr(row, "eo_code")
    eo_description = getattr(row, "eo_description")
    teh_mesto = getattr(row, "teh_mesto")
    gar_no = getattr(row, "gar_no")
    # head_type = getattr(row, "head_type")
    operation_start_date = getattr(row, "operation_start_date")
    # print("eo_code в файле excel из сап ", eo_code)
    # читаем мастер-файл из базы
    eo_master_data=Eo_DB.query.filter_by(eo_code=eo_code).first()
    # если данных нет, то добавляем запись. Если данные есть, то будем далее обновлять
    if eo_master_data == None:
      # new_eo_master_data_record = Eo_DB(be_code=be_code, eo_code=eo_code, eo_description=eo_description, teh_mesto=teh_mesto, gar_no=gar_no)
      new_eo_master_data_record = Eo_DB(be_code=be_code, eo_code=eo_code, eo_description=eo_description, teh_mesto=teh_mesto, gar_no=gar_no, operation_start_date=operation_start_date)
      db.session.add(new_eo_master_data_record)
      db.session.commit()
      print('в мастер-файл добавлена новая запись с eo: ', eo_code)
      # обновляем статус в предыдущих записях лог файла
      # log_data = LogsDB.query.all()
      log_data_updated = LogsDB.query.update(dict(log_status='old'))
      db.session.commit()
      # добавляем новую запись в лог файл
      log_data_new_record = LogsDB(log_text = f"В eo_master_data добавлена запись eo: {eo_code}", log_status = "new")
      db.session.add(log_data_new_record)
      db.session.commit()
    else:
      # данные уже есть
      eo_master_data.eo_description = eo_description
      eo_master_data.teh_mesto = teh_mesto
      # если существующий на текущий момент гаражный номер в базе отличается от того, что записан в загружаемом файле
      # то добавляем в лог новую запись
      if eo_master_data.gar_no != gar_no:
        # проверяем есть ли уже эта запись в таблице конфликтов
        # для проверки сравниваем стринг со стрингом
        current_master_data_gar_no = str(eo_master_data.gar_no)
        uploaded_gar_no_value = str(gar_no)
        
        # ищем запись с этими данными в таблице конфликтов
        gar_no_conflict_record = Eo_data_conflicts.query.filter_by(eo_conflict_field_current_master_data=current_master_data_gar_no, eo_conflict_field_uploaded_data=uploaded_gar_no_value, eo_conflict_status="active").first()
        if gar_no_conflict_record == None:
          new_conflict_record = Eo_data_conflicts(eo_code = eo_code, eo_conflict_field = 'gar_no', eo_conflict_description=f"Гаражный номер в загруженном файле ({gar_no}) не соответствует гаражному номеру в мастер-файле ({eo_master_data.gar_no})", eo_conflict_field_current_master_data = current_master_data_gar_no, eo_conflict_field_uploaded_data=uploaded_gar_no_value)
          db.session.add(new_conflict_record)
          db.session.commit()
          # создаем запись в логах и отдаем ее в интерфейс
          log_data_updated = LogsDB.query.update(dict(log_status='old'))
          db.session.commit()
          # добавляем новую запись в лог файл
          log_data_new_record = LogsDB(log_text = f"Гаражный номер в загруженном файле ({gar_no}) не соответствует гаражному номеру в мастер-файле ({eo_master_data.gar_no})", log_status = "new")
          db.session.add(log_data_new_record)
          db.session.commit()
        
        # если запись о конфликте нашлась, то пишем в лог, но не пишшем в конфликты
        else:
          log_data_updated = LogsDB.query.update(dict(log_status='old'))
          db.session.commit()
          # добавляем новую запись в лог файл
          log_data_new_record = LogsDB(log_text = f"В лог-файле уже есть запись о конфликте. Гаражный номер в загруженном файле ({gar_no}) не соответствует гаражному номеру в мастер-файле ({eo_master_data.gar_no})", log_status = "new")
          db.session.add(log_data_new_record)
          db.session.commit()
          print("уже есть запись о конфликте с гаражным номером в мастер файле: ", current_master_data_gar_no)

      eo_master_data.operation_start_date=operation_start_date

      db.session.commit()
    
        
    



  # переименовываем колонки из sap наименований в master
  



