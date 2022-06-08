import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, Eo_candidatesDB
from initial_values.initial_values import sap_columns_to_master_columns
# from app import app

db = extensions.db

def generate_excel_add_candidates():
  add_candidate_data = Eo_candidatesDB.query.all()
  result_data = []
  for candidate in add_candidate_data:
    temp_dict = {}
    temp_dict['eo_code'] = candidate.eo_code
    temp_dict['eo_description'] = candidate.eo_description
    temp_dict['be_code'] = candidate.be_code
    temp_dict['teh_mesto'] = candidate.teh_mesto
    temp_dict['gar_no'] = candidate.gar_no
    temp_dict['head_type'] = candidate.head_type
    temp_dict['eo_model_id'] = candidate.eo_model_id
    temp_dict['eo_class_code'] = candidate.eo_class_code
    result_data.append(temp_dict)
  excel_add_candidate_df = pd.DataFrame(result_data)
  
  excel_add_candidate_df.to_excel('downloads/add_candidate_df.xlsx', index = False)
    
    

    
    