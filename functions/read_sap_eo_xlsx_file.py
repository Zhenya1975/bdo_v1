import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB
from initial_values.initial_values import sap_columns_to_master_columns
from app import app

db = extensions.db

sap_columns_to_master_columns = sap_columns_to_master_columns
# sap_columns_to_master_columns = {'Единица оборудования': 'eo_code', 'Название технического объекта':'eo_description', 'Техническое место': 'teh_mesto','Поле сортировки':'gar_no'}

def read_sap_eo_xlsx():
  with app.app_context():
    sap_eo_raw_data = pd.read_excel('uploads/sap_eo_data.xlsx', index_col = False, dtype=str)
    
    sap_eo_data = sap_eo_raw_data.rename(columns=sap_columns_to_master_columns)
    # итерируемся по полученному файлу
    for row in sap_eo_data.itertuples():
      # получаем eo_code
      eo_code = getattr(row, "eo_code")
      # print("eo_code в файле excel из сап ", eo_code)
      # читаем мастер-файл из базы
      eo_master_data=Eo_DB.query.filter_by(eo_code=eo_code).first()
      # если данных нет, то добавляем запись. Если данные есть, то будем далее обновлять
      if eo_master_data == None:
        new_eo_master_data_record = Eo_DB(eo_code=eo_code)
        db.session.add(new_eo_master_data_record)
        db.session.commit()
        print('в мастер-файл добавлена новая запись с eo: ', eo_code)

        
    



  # переименовываем колонки из sap наименований в master
  



