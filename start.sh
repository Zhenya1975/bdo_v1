#!/bin/bash
gunicorn --bind 0.0.0.0 --timeout 3000 app:app 
# gunicorn app:app