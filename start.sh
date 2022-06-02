#!/bin/bash
gunicorn --bind 0.0.0.0 app:app
# gunicorn app:app