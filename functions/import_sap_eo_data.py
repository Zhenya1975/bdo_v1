import csv
from models.models import Eo_DB
from extensions import extensions
from app import app

db = extensions.db


def update_sap_eo_data():
  with app.app_context():
    with open('temp_data/sap_eo_data.csv', encoding='utf8') as csvfile:
      sap_eo_data = csv.reader(csvfile)
      header = next(sap_eo_data)
      for row in sap_eo_data:
        be_code = row[0]
        eo_code = row[1]
        temp_eo_code = row[2]
        eo_description = row[3]
        teh_mesto = row[4]
        
        actual_eo_data = Eo_DB.query.filter_by(eo_code=eo_code).first()
        if actual_eo_data:
          actual_eo_data.temp_eo_code = temp_eo_code
          actual_eo_data.eo_description = eo_description
          actual_eo_data.be_code = be_code
          actual_eo_data.teh_mesto = teh_mesto
        else:
          eo_record = Eo_DB(be_code = be_code, eo_code=eo_code, temp_eo_code = temp_eo_code, eo_description = eo_description, teh_mesto=teh_mesto)
          db.session.add(eo_record)
        try:
          db.session.commit()
        except Exception as e:
          print("Не получилось добавить или обновить запись в таблице ЕО. eo_code: ", eo_code, " Ошибка: ", e)
          db.session.rollback()
          
      eo_data = Eo_DB.query.all()
      print("кол-во ео в базе: ", len(eo_data))
      return "результат импорта - в принт"


# update_sap_eo_data()