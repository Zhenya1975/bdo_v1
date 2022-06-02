from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for, abort
from sqlalchemy import desc
from models.models import Eo_DB, Be_DB
from extensions import extensions
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'csv', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

db = extensions.db

# home = Blueprint('home', __name__, template_folder='templates')
home = Blueprint('home', __name__)

@home.route('/')
def home_view():
  eo_data=Eo_DB.query.order_by(Eo_DB.teh_mesto, Eo_DB.be_code).all()
  
  # eo_data.sort_values(['teh_mesto', 'be_description', 'eo_class_code', 'head_eo_model_descr'], inplace=True)
  return render_template('home.html', eo_data = eo_data)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@home.route('/upload', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    # check if the post request has the file part
    
    
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
      uploaded_file.save(os.path.join('uploads', uploaded_file.filename))
      message = f"файл {uploaded_file.filename} загружен"    
      flash(message)
    return redirect(url_for('home.home_view'))
  
  return 'not uploaded'
  