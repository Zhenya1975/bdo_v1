import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts
from initial_values.initial_values import sap_system_status_ban_list, sap_user_status_ban_list
from datetime import datetime
# from app import app
import sqlite3

db = extensions.db

def generate_eo_diagram_data():
  con = sqlite3.connect("database/datab.db")
  # sql = "SELECT * FROM eo_DB JOIN be_DB"
  sql = "SELECT \
  eo_DB.be_code, \
  be_DB.be_description, \
  eo_DB.eo_class_code, \
  eo_class_DB.eo_class_description, \
  models_DB.eo_model_name, \
  models_DB.eo_category_spec, \
  eo_DB.eo_model_id, \
  eo_DB.sap_model_name, \
  eo_DB.sap_maker, \
  eo_DB.teh_mesto, \
  eo_DB.gar_no, \
  eo_DB.sap_gar_no, \
  eo_DB.eo_code, \
  eo_DB.eo_description, \
  eo_DB.head_type, \
  eo_DB.operation_start_date, \
  eo_DB.reported_operation_start_date, \
  eo_DB.expected_operation_period_years, \
  eo_DB.expected_operation_finish_date, \
  eo_DB.sap_planned_finish_operation_date, \
  eo_DB.expected_operation_status_code, \
  eo_DB.sap_system_status, \
  eo_DB.sap_user_status, \
  eo_DB.reported_operation_finish_date, \
  eo_DB.reported_operation_status, \
  eo_DB.reported_operation_status_date, \
  eo_DB.evaluated_operation_finish_date \
  FROM eo_DB \
  LEFT JOIN models_DB ON eo_DB.eo_model_id = models_DB.eo_model_id \
  LEFT JOIN be_DB ON eo_DB.be_code = be_DB.be_code \
  LEFT JOIN eo_class_DB ON eo_DB.eo_class_code = eo_class_DB.eo_class_code \
  LEFT JOIN operation_statusDB ON eo_DB.expected_operation_status_code = operation_statusDB.operation_status_code"


    
  master_eo_df = pd.read_sql_query(sql, con)
  master_eo_df.sort_values(['be_code','teh_mesto'], inplace=True)
  date_time_plug = '31/12/2099 23:59:59'
  date_time_plug = datetime.strptime(date_time_plug, '%d/%m/%Y %H:%M:%S')
  # excel_master_eo_df.to_csv('temp_data/excel_master_eo_df.csv')
  
  master_eo_df['evaluated_operation_finish_date'] = pd.to_datetime(master_eo_df['evaluated_operation_finish_date'])
  
  master_eo_df['operation_start_date'] = pd.to_datetime(master_eo_df['operation_start_date'])

  # year_dict = {2022:'31.12.2022', 2023:'31.12.2023', 2024:'31.12.2024', 2025:'31.12.2025', 2026:'31.12.2026', 2027:'31.12.2027', 2028:'31.12.2028', 2029:'31.12.2029', 2030:'31.12.2030', 2031:'31.12.2031'}
  year_dict = {2022:{'period_start':'01.01.2022', 'period_end':'31.12.2022'}}
  eo_diagram_data_df = pd.DataFrame()
  eo_diagram_data_df['eo_code'] = master_eo_df['eo_code']
  for year, year_data in year_dict.items():
    year_first_date = datetime.strptime(year_data['period_start'], '%d.%m.%Y')
    year_last_date = datetime.strptime(year_data['period_end'], '%d.%m.%Y')

    master_eo_df = master_eo_df.loc[:, ['eo_code', 'be_code', 'head_type', 'be_description', 'eo_class_code', 'eo_class_description', 'eo_category_spec', 'eo_model_name', 'operation_start_date', 'evaluated_operation_finish_date', 'sap_system_status', 'sap_user_status']]

    # выборка в которую попало то что находится в эксплуатации
    eo_master_temp_df = master_eo_df.loc[master_eo_df['operation_start_date'] < year_last_date] 
    eo_master_temp_df = eo_master_temp_df.loc[eo_master_temp_df['evaluated_operation_finish_date'] > year_last_date]
    eo_master_temp_df = eo_master_temp_df.loc[~eo_master_temp_df['sap_system_status'].isin(sap_system_status_ban_list)]
    eo_master_temp_df = eo_master_temp_df.loc[~eo_master_temp_df['sap_user_status'].isin(sap_user_status_ban_list)]
    eo_master_temp_df['year'] = year
    eo_master_temp_df['qty_by_end_of_year'] = 1
    # eo_master_temp_df.astype({"year": int, "qty_by_end_of_year": int})
    eo_diagram_data_df = pd.merge(eo_diagram_data_df, eo_master_temp_df, on='eo_code', how='left')

    # выборка в которой в указанный период было поступление
    eo_master_temp_in_df = master_eo_df.loc[master_eo_df['operation_start_date'] >= year_first_date]
    eo_master_temp_in_df = eo_master_temp_in_df.loc[eo_master_temp_in_df['operation_start_date'] <= year_last_date]
    
    eo_master_temp_in_df = eo_master_temp_in_df.loc[~eo_master_temp_in_df['sap_system_status'].isin(sap_system_status_ban_list)]
    
    eo_master_temp_in_df = eo_master_temp_in_df.loc[~eo_master_temp_in_df['sap_user_status'].isin(sap_user_status_ban_list)]
    
    eo_master_temp_in_df['qty_in'] = 1
    eo_master_temp_in_df = eo_master_temp_in_df.loc[:, ['eo_code', 'qty_in']]
    
    eo_diagram_data_df = pd.merge(eo_diagram_data_df, eo_master_temp_in_df, on='eo_code', how='left')

    
    eo_diagram_data_df.to_csv('temp_data/eo_diagram_data_df.csv')
    
    
    
    
  
  
  eo_diagram_data_df.to_excel('downloads/eo_diagram_data_df.xlsx', index = False)