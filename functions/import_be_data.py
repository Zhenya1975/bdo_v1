import csv
from models.models import Be_DB
from extensions import extensions
from app import app

db = extensions.db


def update_sap_be_data():
  with app.app_context():
    with open('temp_data/be_data.csv', encoding='utf8') as csvfile:
      sap_eo_data = csv.reader(csvfile)
      for row in sap_eo_data:
        be_code = row[0]
        be_description = row[1]
        be_location = row[2]
        actual_be_data = Be_DB.query.filter_by(be_code=be_code).first()
        if actual_be_data:
          actual_be_data.be_description = be_description
          actual_be_data.be_location = be_location
        else:
          be_record = Be_DB(be_code=be_code, be_description = be_description, be_location = be_location)
          db.session.add(be_record)

        try:
          db.session.commit()
        except Exception as e:
          print("Не получилось добавить или обновить запись в таблице БЕ. be_code: ", be_code, " Ошибка: ", e)
          db.session.rollback()
          
      be_data = Be_DB.query.all()
      print("кол-во БЕ в базе: ", len(be_data))
