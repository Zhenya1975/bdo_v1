from extensions import extensions
from datetime import datetime
import pytz

db = extensions.db
utc_now = pytz.utc.localize(datetime.utcnow())
pst_now = utc_now.astimezone(pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y %H:%M:%S")


class Eo_DB(db.Model):
  eo_id = db.Column(db.Integer, primary_key=True)
  eo_code = db.Column(db.String, unique=True)
  temp_eo_code = db.Column(db.String)
  eo_description = db.Column(db.String)
  be_code = db.Column(db.Integer, db.ForeignKey('be_DB.be_code'))
  teh_mesto = db.Column(db.String)
  gar_no = db.Column(db.Integer)
  head_type = db.Column(db.String)
  operation_start_date=db.Column(db.DateTime)
  expected_operation_finish_date = db.Column(db.DateTime)
  eo_model_id = db.Column(db.Integer, db.ForeignKey('models_DB.eo_model_id'))
  eo_class_code = db.Column(db.String, db.ForeignKey('eo_class_DB.eo_class_code'))

class Models_DB(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  eo_model_id = db.Column(db.Integer, unique=True)
  eo_model_name = db.Column(db.String)
  model_data = db.relationship('Eo_DB', backref='model_data')

class Eo_class_DB(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  eo_class_code = db.Column(db.String, unique=True)
  eo_class_description = db.Column(db.String)
  eo_class_data = db.relationship('Eo_DB', backref='eo_class_data')

class Be_DB(db.Model):
  be_id = db.Column(db.Integer, primary_key=True)
  be_code = db.Column(db.Integer, unique=True)
  be_description = db.Column(db.String)
  be_location = db.Column(db.String)
  be_data = db.relationship('Eo_DB', backref='be_data')

class LogsDB(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  log_text = db.Column(db.Text)
  log_date = db.Column(db.String, default=pst_now)
  log_status = db.Column(db.String)
  