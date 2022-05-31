#!/bin/bash
gunicorn --reload --bind 0.0.0.0:80 app:app
# gunicorn app:app