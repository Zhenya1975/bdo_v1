#!/bin/bash
rm database/datab.db
rm -r migrations
flask db init
flask db migrate -m 'init'
flask db upgrade
python db_init_load_data.py