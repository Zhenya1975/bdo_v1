import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB
from initial_values.initial_values import sap_columns_to_master_columns
# from app import app

db = extensions.db

def generate_excel_master_eo():
  eo_master_data = Eo_DB.query.all()
  result_data = []
  for eo_data in eo_master_data:
    temp_dict = {}
    temp_dict['be_code'] = eo_data.be_code
    temp_dict['be_description'] = eo_data.be_data.be_description
    temp_dict['eo_code'] = eo_data.eo_code
    temp_dict['eo_description'] = eo_data.eo_description
    temp_dict['teh_mesto'] = eo_data.teh_mesto
    temp_dict['gar_no'] = eo_data.gar_no
    temp_dict['head_type'] = eo_data.head_type
    
    result_data.append(temp_dict)
  excel_master_eo_df = pd.DataFrame(result_data)
  excel_master_eo_df.sort_values(['be_code', 'teh_mesto'], inplace=True)
  
  
  excel_master_eo_df.to_excel('downloads/eo_master_data.xlsx', index = False)
  