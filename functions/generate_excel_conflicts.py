import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts
from initial_values.initial_values import sap_columns_to_master_columns
# from app import app

db = extensions.db

def generate_excel_conflicts():
  conflicts_data = Eo_data_conflicts.query.all()
  result_data = []
  for conflict in conflicts_data:
    temp_dict = {}
    temp_dict['eo_code'] = conflict.eo_code
    temp_dict['eo_conflict_field'] = conflict.eo_conflict_field
    result_data.append(temp_dict)
  excel_conflicts_df = pd.DataFrame(result_data)
  
  excel_conflicts_df.to_excel('downloads/conflicts.xlsx', index = False)



  # eo_conflict_field = db.Column(db.String)
  # eo_conflict_field_current_master_data = db.Column(db.String)
  # eo_conflict_field_uploaded_data = db.Column(db.String)
  # eo_conflict_description = db.Column(db.Text)
  # eo_conflict_date = db.Column(db.String, default=pst_now)
  # eo_conflict_status = db.Column(db.String, default='active')