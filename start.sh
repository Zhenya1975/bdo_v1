#!/bin/bash
gunicorn --bind 0.0.0.0 app:app --timeout 1200
# gunicorn app:app