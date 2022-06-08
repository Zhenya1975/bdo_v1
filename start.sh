#!/bin/bash
gunicorn --bind 0.0.0.0 app:app --timeout 600
# gunicorn app:app