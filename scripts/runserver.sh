SDMSEPATH="/mdfsvc/SDMS"
PYTHONPATH=$PYTHONPATH:$SDMSEPATH

export PYTHONPATH

nohup python3 ${SDMSEPATH}/manage.py runserver > /dev/null 2>&1 &
