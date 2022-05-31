#!/bin/bash
gunicorn --reload --bind 0.0.0.0 app:app
# gunicorn app:app