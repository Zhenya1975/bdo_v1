from extensions import extensions

db = extensions.db

class EO_DB(db.Model):
  eo_id = db.Column(db.Integer, primary_key=True)
  eo_code = db.Column(db.String, unique=True)
  eo_description = db.Column(db.String)