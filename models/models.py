from extensions import extensions
from datetime import datetime
import pytz

db = extensions.db
utc_now = pytz.utc.localize(datetime.utcnow())
pst_now = utc_now.astimezone(pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y %H:%M:%S")
date_time_plug = '31/12/2199 23:59:59'
date_time_plug = datetime.strptime(date_time_plug, '%d/%m/%Y %H:%M:%S')



class Eo_candidatesDB(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  eo_code = db.Column(db.String)
  temp_eo_code = db.Column(db.String)
  eo_description = db.Column(db.String)
  be_code = db.Column(db.Integer)
  be_description = db.Column(db.String)
  teh_mesto = db.Column(db.String)
  gar_no = db.Column(db.String)
  head_type = db.Column(db.String)
  eo_model_id = db.Column(db.Integer)
  eo_model_name = db.Column(db.String)
  eo_class_code = db.Column(db.String)
  eo_class_description = db.Column(db.String)
  operation_start_date=db.Column(db.DateTime)
  expected_operation_finish_date = db.Column(db.DateTime)
  

class Eo_DB(db.Model):
  eo_id = db.Column(db.Integer, primary_key=True)
  eo_code = db.Column(db.String, unique=True)
  temp_eo_code = db.Column(db.String)
  eo_description = db.Column(db.String)
  be_code = db.Column(db.Integer, db.ForeignKey('be_DB.be_code'))
  teh_mesto = db.Column(db.String)
  gar_no = db.Column(db.String)
  head_type = db.Column(db.String)
  eo_model_id = db.Column(db.Integer, db.ForeignKey('models_DB.eo_model_id'))
  eo_class_code = db.Column(db.String, db.ForeignKey('eo_class_DB.eo_class_code'))
  operation_start_date=db.Column(db.DateTime)
  expected_operation_period_years = db.Column(db.Integer)
  expected_operation_finish_date = db.Column(db.DateTime, default = date_time_plug)
  expected_operation_status_code = db.Column(db.String, db.ForeignKey('operation_statusDB.operation_status_code'))
  expected_operation_status_code_date = db.Column(db.DateTime)
  reported_operation_status = db.Column(db.String)
  reported_operation_finish_date = db.Column(db.DateTime)
  reported_operation_status_code = db.Column(db.String, db.ForeignKey('operation_statusDB.operation_status_code'))
  reported_operation_status_date = db.Column(db.DateTime)
  sap_system_status = db.Column(db.String)
  sap_user_status = db.Column(db.String)
  conflict_data = db.relationship('Eo_data_conflicts', backref='conflict_data')

class Operation_statusDB(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  operation_status_code = db.Column(db.String)
  operation_status_description = db.Column(db.String)
  sap_operation_status = db.Column(db.String)
  expected_operation_status_data = db.relationship('Eo_DB', backref='operation_status_data', foreign_keys="[Eo_DB.expected_operation_status_code]")
  reported_operation_status_data = db.relationship('Eo_DB', backref='reported_status_data', foreign_keys="[Eo_DB.reported_operation_status_code]")



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

class Eo_data_conflicts(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  be_eo_data_row_no = db.Column(db.Integer)
  eo_code = db.Column(db.String, db.ForeignKey('eo_DB.eo_code'))
  eo_conflict_field = db.Column(db.String)
  eo_conflict_field_current_master_data = db.Column(db.String)
  eo_conflict_field_uploaded_data = db.Column(db.String)
  eo_conflict_description = db.Column(db.Text)
  eo_conflict_date = db.Column(db.String, default=pst_now)
  eo_conflict_status = db.Column(db.String, default='active')
  filename = db.Column(db.String)
  sender_email = db.Column(db.String)
  email_date = db.Column(db.String)
  		
