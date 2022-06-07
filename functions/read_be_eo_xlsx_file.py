import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts, Eo_candidatesDB
from initial_values.initial_values import be_data_columns_to_master_columns
from datetime import datetime
# from app import app

db = extensions.db

be_data_columns_to_master_columns = be_data_columns_to_master_columns

def read_be_eo_xlsx():
  # with app.app_context():
  # читаем excel с данными из бизнес-единиц. Проверяем - если нет нужного листа с данными, то отдаем ошибку
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

  # предыдущие данные в лог файле ресетим
  log_data_updated = LogsDB.query.update(dict(log_status='old'))
  db.session.commit()

  for row in be_eo_data.itertuples():
    # получаем eo_code
    be_eo_data_row_no = getattr(row, "be_eo_data_row_no")
    be_data_eo_code = getattr(row, "eo_code")
    be_data_gar_no = str(getattr(row, "gar_no"))

    # читаем мастер-файл из базы
    eo_master_data=Eo_DB.query.filter_by(eo_code=be_data_eo_code).first()
    
    # если данных нет, то добавляем запись в таблицу кандидатов на добавление
    if eo_master_data == None:
      new_eo_candidate_record = Eo_candidatesDB(eo_code=be_data_eo_code, gar_no = be_data_gar_no)
      db.session.add(new_eo_candidate_record)
    # если данные есть, то проверяем на наличие конфликта
    else:
      eo_master_data_garno = eo_master_data.gar_no
      # Если гаражные номера не совпадают, то это новый конфликт
      if eo_master_data_garno != be_data_gar_no:
        new_conflict_record = Eo_data_conflicts(eo_code = be_data_eo_code, eo_conflict_field = "gar_no", eo_conflict_field_current_master_data = eo_master_data_garno, eo_conflict_field_uploaded_data = be_data_gar_no, eo_conflict_description = f"Гаражный номер в файле из БЕ {be_data_gar_no} не соответствует гаражному номеру в мастер-файле {eo_master_data_garno}")
        db.session.add(new_conflict_record)
        # добавляем новую запись в лог файл
        log_data_new_record = LogsDB(log_text = f"Добавлена запись о новом конфликте. В eo_code ({be_data_gar_no}) гаражный номер в загруженном файле ({be_data_gar_no}) не соответствует гаражному номеру в мастер-файле ({eo_master_data_garno})", log_status = "new")
        db.session.add(log_data_new_record)
        print("Создан новый конфликт. eo_code: ", be_data_eo_code, ". Гаражный номер в мастер-файле: ", eo_master_data_garno, ", гаражный номер в загружаемом файле: ", be_data_gar_no)
      # если гаражные номера совпадают, то конфликта нет и движемся дальше
    
    db.session.commit()  
        
      
    



  

  

  
  
  