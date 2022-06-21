import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Eo_calendar_operation_status_DB
from datetime import datetime
from app import app
import sqlite3

db = extensions.db

def read_date(date_input, eo_code):  

  if "timestamp" in str(type(date_input)) or 'datetime' in str(type(date_input)):
    date_output = date_input
    return date_output
  elif "str" in str(type(date_input)):
    try:
      date_output = datetime.strptime(date_input, '%d.%m.%Y')
      return date_output
    except:
      pass
    try:
      date_output = datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S')
      return date_output
    except:
      pass  
    try:
      date_output = datetime.strptime(date_input, '%Y-%m-%d')
      return date_output
    except Exception as e:
      print(f"eo_code: {eo_code}. Не удалось сохранить в дату '{date_input}, тип: {type(date_input)}'. Ошибка: ", e)
      date_output = datetime.strptime('1.1.2199', '%d.%m.%Y')
      return date_output
  
  elif "nat" in str(type(date_input)) or "NaT" in str(type(date_input)) or "float" in str(type(date_input)):
    date_output = datetime.strptime('1.1.2199', '%d.%m.%Y')
    return date_output
  else:
    print(eo_code, "не покрыто типами данных дат", type(date_input), date_input)
    date_output = datetime.strptime('1.1.2199', '%d.%m.%Y')
    return date_output

    
def calendar_operation_status_calc():
  with app.app_context():
    con = sqlite3.connect("database/datab.db")
    cursor = con.cursor()
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
    eo_DB.sap_planned_finish_operation_date, \
    eo_DB.expected_operation_status_code, \
    eo_DB.expected_operation_status_code_date, \
    eo_DB.sap_system_status, \
    eo_DB.sap_user_status, \
    eo_DB.reported_operation_finish_date, \
    eo_DB.reported_operation_status, \
    eo_DB.evaluated_operation_finish_date \
    FROM eo_DB \
    LEFT JOIN models_DB ON eo_DB.eo_model_id = models_DB.eo_model_id \
    LEFT JOIN be_DB ON eo_DB.be_code = be_DB.be_code \
    LEFT JOIN eo_class_DB ON eo_DB.eo_class_code = eo_class_DB.eo_class_code \
    LEFT JOIN operation_statusDB ON eo_DB.expected_operation_status_code = operation_statusDB.operation_status_code"
    
    master_eo_df = pd.read_sql_query(sql, con)
    master_eo_df.sort_values(['be_code','teh_mesto'], inplace=True)
  
    master_eo_df['operation_start_date'] = pd.to_datetime(master_eo_df['operation_start_date'])
    master_eo_df['sap_planned_finish_operation_date'] = pd.to_datetime(master_eo_df['sap_planned_finish_operation_date'])
    master_eo_df['evaluated_operation_finish_date'] = pd.to_datetime(master_eo_df['evaluated_operation_finish_date'])
    master_eo_df['reported_operation_finish_date'] = pd.to_datetime(master_eo_df['reported_operation_finish_date'])
    master_eo_df['sap_system_status'].fillna("plug", inplace = True)
    master_eo_df['sap_user_status'].fillna("plug", inplace = True)
  
    for row in master_eo_df.itertuples():
      index_value = getattr(row, 'Index')
      eo_code = getattr(row, "eo_code")
      operation_start_date = getattr(row, "operation_start_date") 
      sap_planned_finish_operation_date = getattr(row, "sap_planned_finish_operation_date") 
      evaluated_operation_finish_date = getattr(row, "evaluated_operation_finish_date")
      sap_system_status = getattr(row, "sap_system_status")
      sap_user_status = getattr(row, "sap_user_status")
      reported_operation_finish_date = getattr(row, "reported_operation_finish_date")
      # print(eo_code, "reported_operation_finish_date: ", reported_operation_finish_date, "evaluated_operation_finish_date: ", evaluated_operation_finish_date)
  
      if 'nat' not in str(type(sap_planned_finish_operation_date)):
        evaluated_operation_finish_date = sap_planned_finish_operation_date
        update_evaluated_operation_finish_date_sql = f"UPDATE eo_DB SET evaluated_operation_finish_date='{evaluated_operation_finish_date}' WHERE eo_code='{eo_code}';"
        # print(update_evaluated_operation_finish_date_sql)
        cursor.execute(update_evaluated_operation_finish_date_sql)
        con.commit()
      
      if 'nat' not in str(type(reported_operation_finish_date)):
        # print(reported_operation_finish_date)
        evaluated_operation_finish_date = reported_operation_finish_date
        update_evaluated_operation_finish_date_sql = f"UPDATE eo_DB SET evaluated_operation_finish_date='{evaluated_operation_finish_date}' WHERE eo_code='{eo_code}';"
        # print(update_evaluated_operation_finish_date_sql)
        cursor.execute(update_evaluated_operation_finish_date_sql)
        con.commit()
      age_date = datetime.strptime('01.07.2022', '%d.%m.%Y')
      if age_date > operation_start_date and age_date < evaluated_operation_finish_date and 'МТКУ' not in sap_system_status and 'КОНС' not in sap_user_status:
        calendar_record = Eo_calendar_operation_status_DB.query.filter_by(eo_code = eo_code).first()
        if calendar_record:
          calendar_record.july_2022_qty = 1
          db.session.commit()
        else:
          new_eo_record = Eo_calendar_operation_status_DB(eo_code = eo_code, july_2022_qty = 1)
          db.session.add(new_eo_record)
          db.session.commit()
      else:
        calendar_record = Eo_calendar_operation_status_DB.query.filter_by(eo_code = eo_code).first()
        if calendar_record:
          calendar_record.july_2022_qty = 0
          db.session.commit()
        else:
          new_eo_record = Eo_calendar_operation_status_DB(eo_code = eo_code, july_2022_qty = 0)
          db.session.add(new_eo_record)
          db.session.commit()
        