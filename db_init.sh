#!/bin/bash
python db_backup.py
rm database/datab.db
rm -r migrations
flask db init
flask db migrate -m 'init'
flask db upgrade
# python db_init_load_data.py

python db_restore.py