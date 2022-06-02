import pandas as pd
from models.models import Eo_DB, Be_DB
from initial_values.initial_values import sap_columns_to_master_columns
from app import app

sap_columns_to_master_columns = sap_columns_to_master_columns
# sap_columns_to_master_columns = {'Единица оборудования': 'eo_code', 'Название технического объекта':'eo_description', 'Техническое место': 'teh_mesto','Поле сортировки':'gar_no'}

def read_sap_eo_xlsx():
  with app.app_context():
    sap_eo_raw_data = pd.read_excel('uploads/sap_eo_data.xlsx', index_col = False, dtype=str)
    sap_eo_data = sap_eo_raw_data.rename(columns=sap_columns_to_master_columns)
    # читаем мастер-файл из базы
    eo_master_data=Eo_DB.query.all()

  

  # переименовываем колонки из sap наименований в master
  



