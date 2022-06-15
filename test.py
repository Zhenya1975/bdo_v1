import pandas as pd
from extensions import extensions
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts, Eo_candidatesDB
from initial_values.initial_values import be_data_columns_to_master_columns
from datetime import datetime
from app import app
import sqlite3
from sqlalchemy import create_engine
import os

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
delete_record()    