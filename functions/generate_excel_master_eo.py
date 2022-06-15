import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts
from initial_values.initial_values import sap_columns_to_master_columns
from datetime import datetime
# from app import app
import sqlite3

db = extensions.db

def sql_to_eo_master():
  con = sqlite3.connect("database/datab.db")
  # sql = "SELECT * FROM eo_DB JOIN be_DB"
  sql = "SELECT \
  eo_DB.be_code, \
  be_DB.be_description, \
  eo_DB.eo_class_code, \
  eo_class_DB.eo_class_description, \
  models_DB.eo_model_name, \
  eo_DB.teh_mesto, \
  eo_DB.gar_no, \
  eo_DB.eo_code, \
  eo_DB.head_type, \
  eo_DB.operation_start_date, \
  eo_DB.expected_operation_period_years, \
  eo_DB.expected_operation_finish_date, \
  eo_DB.expected_operation_status_code, \
  operation_statusDB.operation_status_description, \
  eo_DB.expected_operation_status_code_date \
  FROM eo_DB \
  LEFT JOIN models_DB ON eo_DB.eo_model_id = models_DB.eo_model_id \
  LEFT JOIN be_DB ON eo_DB.be_code = be_DB.be_code \
  LEFT JOIN eo_class_DB ON eo_DB.eo_class_code = eo_class_DB.eo_class_code \
  LEFT JOIN operation_statusDB ON eo_DB.expected_operation_status_code = operation_statusDB.operation_status_code"
  
  excel_master_eo_df = pd.read_sql_query(sql, con)
  date_time_plug = '31/12/2199 23:59:59'
  date_time_plug = datetime.strptime(date_time_plug, '%d/%m/%Y %H:%M:%S')
  excel_master_eo_df['expected_operation_finish_date'] = pd.to_datetime(excel_master_eo_df['expected_operation_finish_date'])
  excel_master_eo_df['operation_start_date'] = pd.to_datetime(excel_master_eo_df['operation_start_date'])
  excel_master_eo_df['expected_operation_status_code_date'] = pd.to_datetime(excel_master_eo_df['expected_operation_status_code_date'])
  
  excel_master_eo_df_subset = excel_master_eo_df.loc[excel_master_eo_df['expected_operation_finish_date'] == date_time_plug]
  indexes = excel_master_eo_df_subset.index.values
  excel_master_eo_df.loc[indexes, ['expected_operation_finish_date']] = ""
  
  excel_master_eo_df_2_subset = excel_master_eo_df.loc[excel_master_eo_df['operation_start_date'] == date_time_plug]
  indexes_2 = excel_master_eo_df_2_subset.index.values
  excel_master_eo_df.loc[indexes_2, ['operation_start_date']] = ""

  excel_master_eo_df["operation_start_date"] = excel_master_eo_df["operation_start_date"].dt.strftime("%d.%m.%Y")

  excel_master_eo_df["expected_operation_finish_date"] = excel_master_eo_df["expected_operation_finish_date"].dt.strftime("%d.%m.%Y")
  
  excel_master_eo_df["expected_operation_status_code_date"] = excel_master_eo_df["expected_operation_status_code_date"].dt.strftime("%d.%m.%Y")


  
  excel_master_eo_df.to_excel('downloads/eo_master_data.xlsx', index = False)  



def conflict_list_prepare(eo_code):
  conflict_data = Eo_data_conflicts.query.filter_by(eo_code = eo_code, eo_conflict_status = "active")
  conflict_list = []
  for conflict in conflict_data:
    conflict_id = conflict.id
    conflict_list.append(conflict_id)
  return conflict_list

def generate_excel_master_eo():
  
  eo_master_data = Eo_DB.query.all()
  if len(list(eo_master_data))>0:
    result_data = []
    for eo_data in eo_master_data:
      temp_dict = {}
      temp_dict['be_code'] = eo_data.be_code
      temp_dict['be_description'] = eo_data.be_data.be_description
      try:
        temp_dict['eo_class_code'] = eo_data.eo_class_code
        temp_dict['eo_class_description'] = eo_data.eo_class_data.eo_class_description
      except:
        pass
      temp_dict['eo_code'] = eo_data.eo_code
      temp_dict['eo_description'] = eo_data.eo_description
      try:
        temp_dict['eo_model_id'] = eo_data.eo_model_id
        temp_dict['eo_model_name'] = eo_data.model_data.eo_model_name
      except:
        pass
      temp_dict['teh_mesto'] = eo_data.teh_mesto
      temp_dict['gar_no'] = eo_data.gar_no
      temp_dict['head_type'] = eo_data.head_type
      operation_start_date = eo_data.operation_start_date.strftime("%d.%m.%Y")
      temp_dict['operation_start_date'] = operation_start_date
      expected_operation_finish_date = eo_data.expected_operation_finish_date.strftime("%d.%m.%Y")
      if expected_operation_finish_date == '31.12.2199':
        temp_dict['expected_operation_finish_date'] = ""
      else:
        temp_dict['expected_operation_finish_date'] = expected_operation_finish_date
      conflict_list = conflict_list_prepare(eo_data.eo_code)
      temp_dict['eo_active_conflicts_ids'] = conflict_list
      
      result_data.append(temp_dict)
    excel_master_eo_df = pd.DataFrame(result_data)
    excel_master_eo_df.sort_values(['be_code','teh_mesto'], inplace=True)
  else:
    excel_master_eo_df = pd.DataFrame(columns=['be_code', 'be_description', 'eo_class_code', 'eo_class_description', 'eo_code', 'eo_description', 'eo_model_id', 'eo_model_name', 'teh_mesto', 'gar_no', 'head_type', 'operation_start_date', 'expected_operation_finish_date'])
  
  excel_master_eo_df.to_excel('downloads/eo_master_data.xlsx', index = False)  

									
