import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB
from initial_values.initial_values import sap_columns_to_master_columns
# from app import app

db = extensions.db

sap_columns_to_master_columns = sap_columns_to_master_columns

def read_sap_eo_xlsx():
  # with app.app_context():
  sap_eo_raw_data = pd.read_excel('uploads/sap_eo_data.xlsx', index_col = False, dtype=str)
  
  sap_eo_data = sap_eo_raw_data.rename(columns=sap_columns_to_master_columns)
  # print(sap_eo_data.info())
  # итерируемся по полученному файлу
  for row in sap_eo_data.itertuples():
    # получаем eo_code
    be_code = getattr(row, "be_code")
    eo_code = getattr(row, "eo_code")
    eo_description = getattr(row, "eo_description")
    teh_mesto = getattr(row, "teh_mesto")
    gar_no = getattr(row, "gar_no")
    # print("eo_code в файле excel из сап ", eo_code)
    # читаем мастер-файл из базы
    eo_master_data=Eo_DB.query.filter_by(eo_code=eo_code).first()
    # если данных нет, то добавляем запись. Если данные есть, то будем далее обновлять
    if eo_master_data == None:
      # new_eo_master_data_record = Eo_DB(be_code=be_code, eo_code=eo_code, eo_description=eo_description, teh_mesto=teh_mesto, gar_no=gar_no)
      new_eo_master_data_record = Eo_DB(be_code=be_code, eo_code=eo_code, eo_description=eo_description, teh_mesto=teh_mesto, gar_no=gar_no)
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
      print('данные уже есть')
        
    



  # переименовываем колонки из sap наименований в master
  



