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
    date_plug = datetime.strptime('1.1.2199', '%d.%m.%Y')
    master_eo_df['sap_planned_finish_operation_date'].fillna(date_plug, inplace = True)
    master_eo_df['reported_operation_finish_date'].fillna(date_plug, inplace = True)
    master_eo_df['evaluated_operation_finish_date'].fillna(date_plug, inplace = True)
    master_eo_df['sap_system_status'].fillna("plug", inplace = True)
    master_eo_df['sap_user_status'].fillna("plug", inplace = True)


    ###################### Обновление списке ео в calendar_operation_status_eo ###########################
    sql_calendar_operation_status = "SELECT eo_calendar_operation_status_DB.eo_code FROM eo_calendar_operation_status_DB"
    calendar_operation_status_df = pd.read_sql_query(sql_calendar_operation_status, con)
    calendar_operation_status_eo_list = list(calendar_operation_status_df['eo_code'])

    calendar_operation_status_eo_list_add_df = master_eo_df.loc[~master_eo_df['eo_code'].isin(calendar_operation_status_eo_list)]
    calendar_operation_status_eo_list_add = list(calendar_operation_status_eo_list_add_df['eo_code'])
    if len(calendar_operation_status_eo_list_add)>0:
      for eo_to_add in calendar_operation_status_eo_list_add:
        insert_calendar_sql = f"INSERT INTO eo_calendar_operation_status_DB (eo_code) VALUES ({eo_to_add});"
        cursor.execute(insert_calendar_sql)
        con.commit() 

    # В поле  evaluated_operation_finish_date  указываем значение из expected_operation_finish_date
    master_eo_filtered_df = master_eo_df.loc[master_eo_df['evaluated_operation_finish_date'] ==date_plug]
    indexes = list(master_eo_filtered_df.index.values)
    master_eo_df.loc[indexes, ['evaluated_operation_finish_date']] = master_eo_df['expected_operation_finish_date']
    
    # выборка в которой пусто в колонке sap_planned_finish_operation_date
    master_eo_filtered_df_2 = master_eo_df.loc[master_eo_df['sap_planned_finish_operation_date'] != date_plug]
    # print(master_eo_filtered_df_2['sap_planned_finish_operation_date'])
    indexes = list(master_eo_filtered_df_2.index.values)
    dates_list_df = master_eo_df.loc[indexes, ['sap_planned_finish_operation_date']]
    master_eo_df.loc[indexes, ['evaluated_operation_finish_date']] = list(dates_list_df['sap_planned_finish_operation_date'])

    master_eo_filtered_df_3 = master_eo_df.loc[master_eo_df['reported_operation_finish_date'] != date_plug]
    indexes_3 = list(master_eo_filtered_df_3.index.values)
    dates_list_df_3 = master_eo_df.loc[indexes_3, ['reported_operation_finish_date']]
    master_eo_df.loc[indexes_3, ['evaluated_operation_finish_date']] = list(dates_list_df_3['reported_operation_finish_date'])


    
    for row in master_eo_df.itertuples():
      evaluated_operation_finish_date = getattr(row, "evaluated_operation_finish_date")
      eo_code = getattr(row, "eo_code")
      update_calendar_sql = f"UPDATE eo_DB SET evaluated_operation_finish_date = '{evaluated_operation_finish_date}' WHERE eo_code = '{eo_code}';"
      cursor.execute(update_calendar_sql)
      con.commit() 

    
    master_eo_df.to_csv('temp_data/master_eo_df.csv')

    # обработка данных без итераций
        
    
    calendar_list = ['july_2022', 'august_2022']
    qty_column_name = 'july_2022_qty'
    qty_in_column_name = 'july_2022_in'
    qty_out_column_name = 'july_2022_out'
    for calendar_point in calendar_list:
      if calendar_point == 'july_2022':
        age_date = datetime.strptime('31.07.2022', '%d.%m.%Y')
        period_begin = datetime.strptime('01.07.2022', '%d.%m.%Y')
        qty_column_name = 'july_2022_qty'
        qty_in_column_name = 'july_2022_in'
        qty_out_column_name = 'july_2022_out'
      elif  calendar_point == 'august_2022': 
        age_date = datetime.strptime('31.08.2022', '%d.%m.%Y')
        period_begin = datetime.strptime('01.08.2022', '%d.%m.%Y')
        qty_column_name = 'august_2022_qty'
        qty_in_column_name = 'august_2022_in'
        qty_out_column_name = 'august_2022_out'

      eo_master_temp_df = master_eo_df.loc[master_eo_df['operation_start_date'] < age_date] 
      eo_master_temp_df = eo_master_temp_df.loc[eo_master_temp_df['evaluated_operation_finish_date'] > age_date]
      

      for row in eo_master_temp_df.itertuples():
        eo = getattr(row, 'eo_code')
        evaluated_operation_finish_date = getattr(row, 'evaluated_operation_finish_date')
        
        update_calendar_sql = f"UPDATE eo_DB SET evaluated_operation_finish_date = '{evaluated_operation_finish_date}' WHERE eo_code = '{eo}';"
        cursor.execute(update_calendar_sql)
        con.commit() 

      # if age_date > operation_start_date and age_date < evaluated_operation_finish_date and 'МТКУ' not in sap_system_status and 'КОНС' not in sap_user_status:
      #   calendar_record = Eo_calendar_operation_status_DB.query.filter_by(eo_code = eo_code).first()
      #   if calendar_record:
      #     update_calendar_sql = f"UPDATE eo_calendar_operation_status_DB SET '{qty_column_name}'=1 WHERE eo_code='{eo_code}';"
      #     cursor.execute(update_calendar_sql)
      #     con.commit()  
      #   else:
      #     update_calendar_sql = f"INSERT INTO eo_calendar_operation_status_DB SET (eo_code, '{qty_column_name}') VALUES ({eo_code}, 1);"
      #     cursor.execute(update_calendar_sql)
      #     con.commit() 
        
      # # ЕСЛИ ДАТА НЕ ПОПАЛА МЕЖДУ НАЧАЛОМ И КОНЦОМ ЭКСПЛУАТАЦИИ
      # else:
      #   calendar_record = Eo_calendar_operation_status_DB.query.filter_by(eo_code = eo_code).first()
      #   if calendar_record:
      #     update_calendar_sql = f"UPDATE eo_calendar_operation_status_DB SET '{qty_column_name}'=0 WHERE eo_code='{eo_code}';"
      #     cursor.execute(update_calendar_sql)
      #     con.commit() 
      #   else:
      #     update_calendar_sql = f"INSERT INTO eo_calendar_operation_status_DB SET \
      #     (eo_code, '{qty_column_name}') VALUES \
      #     ({eo_code}, 0);"
      #     cursor.execute(update_calendar_sql)
      #     con.commit() 
      
      # # Заполнение колонки поступлений
      # # если дата начала эксплуатации попадает в период    
      # if operation_start_date > period_begin and operation_start_date < age_date and 'МТКУ' not in sap_system_status and 'КОНС' not in sap_user_status:
      #   calendar_record = Eo_calendar_operation_status_DB.query.filter_by(eo_code = eo_code).first()
      #   # если запись в календарном плане уже есть, то обновляем
      #   if calendar_record:
      #     update_calendar_sql = f"UPDATE eo_calendar_operation_status_DB SET '{qty_in_column_name}'=1 WHERE eo_code='{eo_code}';"
      #     cursor.execute(update_calendar_sql)
      #     con.commit() 
      #   else:
      #     update_calendar_sql = f"INSERT INTO eo_calendar_operation_status_DB SET (eo_code, '{qty_in_column_name}') VALUES ({eo_code}, 1);"
      #     cursor.execute(update_calendar_sql)
      #     con.commit() 
      # else:
      #   calendar_record = Eo_calendar_operation_status_DB.query.filter_by(eo_code = eo_code).first()
      #   # если запись в календарном плане уже есть, то обновляем
      #   if calendar_record:
      #     update_calendar_sql = f"UPDATE eo_calendar_operation_status_DB SET '{qty_in_column_name}'=0 WHERE eo_code='{eo_code}';"
      #     cursor.execute(update_calendar_sql)
      #     con.commit() 
      #   else:
      #     update_calendar_sql = f"INSERT INTO eo_calendar_operation_status_DB SET (eo_code, '{qty_in_column_name}') VALUES ({eo_code}, 0);"
      #     cursor.execute(update_calendar_sql)
      #     con.commit() 

      # # Заполнение колонки убытий  
      # if evaluated_operation_finish_date > period_begin and evaluated_operation_finish_date < age_date:
      #   calendar_record = Eo_calendar_operation_status_DB.query.filter_by(eo_code = eo_code).first()
      #   # если запись в календарном плане уже есть, то обновляем
      #   if calendar_record:
      #     update_calendar_sql = f"UPDATE eo_calendar_operation_status_DB SET '{qty_out_column_name}'=1 WHERE eo_code='{eo_code}';"
      #     cursor.execute(update_calendar_sql)
      #     con.commit() 
      #   else:
      #     update_calendar_sql = f"INSERT INTO eo_calendar_operation_status_DB SET (eo_code, '{qty_out_column_name}') VALUES ({eo_code}, 1);"
      #     cursor.execute(update_calendar_sql)
      #     con.commit() 
      # else:
      #   calendar_record = Eo_calendar_operation_status_DB.query.filter_by(eo_code = eo_code).first()
      #   # если запись в календарном плане уже есть, то обновляем
      #   if calendar_record:
      #     update_calendar_sql = f"UPDATE eo_calendar_operation_status_DB SET '{qty_out_column_name}'=0 WHERE eo_code='{eo_code}';"
      #     cursor.execute(update_calendar_sql)
      #     con.commit() 
      #   else:
      #     update_calendar_sql = f"INSERT INTO eo_calendar_operation_status_DB SET (eo_code, '{qty_out_column_name}') VALUES ({eo_code}, 0);"
      #     cursor.execute(update_calendar_sql)
      #     con.commit() 