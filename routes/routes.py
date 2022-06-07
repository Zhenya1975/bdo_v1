from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for, abort, send_file
from sqlalchemy import desc
import pandas as pd
from models.models import Eo_DB, Be_DB, LogsDB, Eo_data_conflicts
from extensions import extensions
from initial_values.initial_values import sap_columns_to_master_columns
from werkzeug.utils import secure_filename
import os
from functions import read_sap_eo_xlsx_file, read_be_eo_xlsx_file, generate_excel_master_eo, generate_excel_conflicts


UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'csv', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

db = extensions.db

# home = Blueprint('home', __name__, template_folder='templates')
home = Blueprint('home', __name__)

@home.route('/')
def home_view():
  eo_data=Eo_DB.query.order_by(Eo_DB.teh_mesto, Eo_DB.be_code).all()
  log_data = LogsDB.query.filter_by(log_status = "new").all()
  conflicts_data = Eo_data_conflicts.query.filter_by(eo_conflict_status="active").all()
  number_of_active_conflicts = len(list(conflicts_data))

  # eo_data.sort_values(['teh_mesto', 'be_description', 'eo_class_code', 'head_eo_model_descr'], inplace=True)
  return render_template('home.html', eo_data = eo_data, log_data=log_data, number_of_active_conflicts=number_of_active_conflicts)


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
  ALLOWED_EXTENSIONS = {'xlsx','csv'}  
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@home.route('/upload_be_eo_file', methods=['GET', 'POST'])
def upload_be_eo_file():
  if request.method == 'POST':
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
      message = f"файл с пустым именем"
      flash(message, 'alert-danger')
      return redirect(url_for('home.home_view'))
    
    elif allowed_file(uploaded_file.filename) == False:
      message = f"Неразрешенное расширение файла {uploaded_file.filename}"
      flash(message, 'alert-danger')
      return redirect(url_for('home.home_view'))

    elif "be_eo_data" not in uploaded_file.filename:
      message = "В имени файла нет текста be_eo_data"
      flash(message, 'alert-danger')    
      return redirect(url_for('home.home_view'))

    elif "xlsx" not in uploaded_file.filename:
      message = "В имени файла нет расширения xlsx"
      flash(message, 'alert-danger')    
      return redirect(url_for('home.home_view'))

    
    else:    
      uploaded_file.save(os.path.join('uploads', "be_eo_data.xlsx"))
      message = f"файл {uploaded_file.filename} загружен"
      print(f"файл {uploaded_file.filename} загружен")
      read_be_eo_xlsx_file.read_be_eo_xlsx()
      flash(message, 'alert-success')
      return redirect(url_for('home.home_view'))

      
    return 'not uploaded'

@home.route('/upload_sap_eo_file', methods=['GET', 'POST'])
def upload_sap_eo_file():
  if request.method == 'POST':
    # check if the post request has the file part
  
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
      message = f"файл с пустым именем"
      flash(message, 'alert-danger')
      return redirect(url_for('home.home_view'))
    elif allowed_file(uploaded_file.filename) == False:
      message = f"Неразрешенное расширение файла {uploaded_file.filename}"
      flash(message, 'alert-danger')
      return redirect(url_for('home.home_view'))
    elif "sap_eo_data" not in uploaded_file.filename:
      message = "В имени файла нет текста sap_eo_data"
      flash(message, 'alert-danger')    
      return redirect(url_for('home.home_view'))
    elif "xlsx" not in uploaded_file.filename:
      message = "В имени файла нет расширения xlsx"
      flash(message, 'alert-danger')    
      return redirect(url_for('home.home_view'))
    else:    
      # uploaded_file.save(os.path.join('uploads', uploaded_file.filename))
      uploaded_file.save(os.path.join('uploads', "sap_eo_data.xlsx"))
      message = f"файл {uploaded_file.filename} загружен"
      read_sap_eo_xlsx_file.read_sap_eo_xlsx()
      flash(message, 'alert-success')
    return redirect(url_for('home.home_view'))
  
  return 'not uploaded'



@home.route('/download_be_data_template', methods=['GET', 'POST'])
def download_be_data_template():
  if request.method == 'POST':    
    return send_file("downloads/be_eo_data_template.xlsx", as_attachment=True) 
  return 'not downloaded be_eo_data_template'


@home.route('/download_master_eo_file', methods=['GET', 'POST'])
def download_master_eo_file():
  if request.method == 'POST':
    
    # выпекаем excel-файл из базы данных
    try:
      generate_excel_master_eo.generate_excel_master_eo()
    except Exception as e:
      print("не удалось создать excel файл eo_master_data.xlsx. Ошибка: ", e)
      
    return send_file("downloads/eo_master_data.xlsx", as_attachment=True) 

@home.route('/conflicts', methods=['GET', 'POST'])
def conflicts():
  if request.method == 'POST':
    
    # выпекаем excel-файл из базы данных
    generate_excel_conflicts.generate_excel_conflicts()

    return send_file("downloads/conflicts.xlsx", as_attachment=True) 

    

