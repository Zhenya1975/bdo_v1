from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for, abort
from sqlalchemy import desc
from models.models import EO_DB
from extensions import extensions

db = extensions.db

home = Blueprint('home', __name__, template_folder='templates')