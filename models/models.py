from extensions import extensions

db = extensions.db

class Eo_DB(db.Model):
  eo_id = db.Column(db.Integer, primary_key=True)
  eo_code = db.Column(db.String, unique=True)
  temp_eo_code = db.Column(db.String)
  eo_description = db.Column(db.String)
  be_code = db.Column(db.Integer, db.ForeignKey('be_DB.be_code'))
  teh_mesto = db.Column(db.String)

class Be_DB(db.Model):
  be_id = db.Column(db.Integer, primary_key=True)
  be_code = db.Column(db.Integer, unique=True)
  be_description = db.Column(db.String)
  be_location = db.Column(db.String)
  be_data = db.relationship('Eo_DB', backref='be_data')

