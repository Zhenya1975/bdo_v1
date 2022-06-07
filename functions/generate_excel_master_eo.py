import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB
from initial_values.initial_values import sap_columns_to_master_columns
# from app import app

db = extensions.db

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
      
      result_data.append(temp_dict)
    excel_master_eo_df = pd.DataFrame(result_data)
    excel_master_eo_df.sort_values(['be_code','teh_mesto', 'eo_model_name'], inplace=True)
  else:
    excel_master_eo_df = pd.DataFrame(columns=['be_code', 'be_description', 'eo_class_code', 'eo_class_description', 'eo_code', 'eo_description', 'eo_model_id', 'eo_model_name', 'teh_mesto', 'gar_no', 'head_type', 'operation_start_date', 'expected_operation_finish_date'])
  
  excel_master_eo_df.to_excel('downloads/eo_master_data.xlsx', index = False)  

									
