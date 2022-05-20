# This script will duplicate the backup database
# and run the python script
#
# This is meant for linux (hence .sh)

BACKUP_DB="FIADB_NJ_BACKUP.db"
ACTUAL_DB="FIADB_NJ.db"
PY_SCRIPT="DBRebuild_Main.py"

cp --force $BACKUP_DB $ACTUAL_DB
python3 $PY_SCRIPT
