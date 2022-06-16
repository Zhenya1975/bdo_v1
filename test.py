import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts, Eo_candidatesDB
from initial_values.initial_values import be_data_columns_to_master_columns
from datetime import datetime
from app import app
import sqlite3
from sqlalchemy import create_engine
import os
import pytz

# print(pytz.all_timezones)
# today_datetime = datetime.now(pytz.timezone('Europe/Moscow'))


db = extensions.db

def delete_alembic_version_table():
  with app.app_context():
    con = sqlite3.connect("database/datab.db")
    # sql = "SELECT * FROM eo_DB JOIN be_DB"
    # sql = "SELECT eo_DB.be_code, models_DB.eo_model_name  FROM eo_DB JOIN models_DB ON eo_DB.eo_model_id = models_DB.eo_model_id"
    cursor = con.cursor()
    drop_table_sql = "DROP TABLE alembic_version"
    cursor.execute(drop_table_sql)
    con.commit()
    cursor.close()

# delete_alembic_version_table()

# delete record from eo

def delete_record():
  with app.app_context():
    con = sqlite3.connect("database/datab.db")
    # sql = "SELECT * FROM eo_DB JOIN be_DB"
    # sql = "SELECT eo_DB.be_code, models_DB.eo_model_name  FROM eo_DB JOIN models_DB ON eo_DB.eo_model_id = models_DB.eo_model_id"
    cursor = con.cursor()
    delete_records_sql = "DELETE FROM eo_DB WHERE eo_code='не присвоен';"
    cursor.execute(delete_records_sql)
    con.commit()
    cursor.close()
# delete_record()    

def delete_eo_records():
  eo_to_delete_df = pd.read_excel('temp_data/delete_eo.xlsx', index_col = False, dtype=str)
  for row in eo_to_delete_df.itertuples():
    eo_code = getattr(row, "eo_code")
    with app.app_context():
      con = sqlite3.connect("database/datab.db")
      cursor = con.cursor()
      # delete_records_sql = f"DELETE FROM eo_DB WHERE eo_code={eo_code};"
      delete_records_sql = f"DELETE FROM eo_DB WHERE eo_code is null;"
      cursor.execute(delete_records_sql)
      con.commit()
      cursor.close()
    
    
delete_eo_records()


def insert_record():
  with app.app_context():
    con = sqlite3.connect("database/datab.db")
    cursor = con.cursor()
    insert_record_sql = "INSERT INTO operation_statusDB (operation_status_code, operation_status_description, sap_operation_status) VALUES ('out_of_operation', 'удалено', 'МТКУ');"
    cursor.execute(insert_record_sql)
    con.commit()
    cursor.close()
  
# insert_record()
def update_record():
  with app.app_context():
    con = sqlite3.connect("database/datab.db")
    cursor = con.cursor()
    update_record_sql = "UPDATE operation_statusDB SET sap_operation_status='' WHERE id= 4;"
    cursor.execute(update_record_sql)
    con.commit()
    cursor.close()

# update_record()

def clear_column_records():
  with app.app_context():
    con = sqlite3.connect("database/datab.db")
    cursor = con.cursor()
    update_record_sql = "UPDATE eo_DB SET reported_operation_finish_date=NULL, reported_operation_status_code = NULL, reported_operation_status_date = NULL, reported_operation_status = NULL;"
    
    cursor.execute(update_record_sql)
    con.commit()
    cursor.close()
    
# clear_column_records()

# UPDATE Table1
# SET    Col1 = NULL
# WHERE  Col2 = 'USA'