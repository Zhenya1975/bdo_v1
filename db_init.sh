#!/bin/bash
rm database/datab.db
rm -r migrations
flask db init
flask db migrate -m 'init'
flask db upgrade
python func.py