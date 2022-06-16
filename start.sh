#!/bin/bash
gunicorn --bind 0.0.0.0 --timeout 2000 app:app 
# gunicorn app:app