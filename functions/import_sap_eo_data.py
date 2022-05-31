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
        eo_record = EO_DB(eo_code=row[0], eo_description = row[1])
        db.session.add(eo_record)
        try:
          db.session.commit()
        except Exception as e:
          print("Не получилось импортировать eo. Ошибка: ", e)
          db.session.rollback()
      eo_data = EO_DB.query.all()
      print("eo импортированы: ", len(eo_data))
      return "результат импорта - в принт"


# update_sap_eo_data()