import csv
from models.models import EO_DB
from extensions import extensions
from app import app

db = extensions.db


def update_sap_eo_data():
  with app.app_context():
    with open('temp_data/sap_eo_data.csv', encoding='utf8') as csvfile:
      sap_eo_data = csv.reader(csvfile)
      for row in sap_eo_data:
        eo_code = row[0]
        eo_description = row[1]
        actual_eo_data = EO_DB.query.filter_by(eo_code=eo_code).first()
        if actual_eo_data:
          actual_eo_data.eo_description = eo_description
        else:
          eo_record = EO_DB(eo_code=eo_code, eo_description = eo_description)
          db.session.add(eo_record)
        try:
          db.session.commit()
        except Exception as e:
          print("Не получилось добавить или обновить запись в таблице ЕО. eo_code: ", eo_code, " Ошибка: ", e)
          db.session.rollback()
          
      eo_data = EO_DB.query.all()
      print("кол-во ео в базе: ", len(eo_data))
      return "результат импорта - в принт"


# update_sap_eo_data()