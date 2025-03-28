#!/bin/bash

NAME="myproject"                     # Name of the application
DJANGODIR= /home/ubuntu/workspace/HOTi/hoti # Django project directory
SOCKFILE=/home/ubuntu/workspace/HOTi/run/gunicorn.sock # we will communicte using this unix socket
USER=ubuntu                              # the user to run as
GROUP=www-data                                 # the group to run as
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=hoti.settings             # which settings file should Django use
DJANGO_WSGI_MODULE=hoti.wsgi                     # WSGI module name

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
source /home/ubuntu/workspace/djangoenv/bin/activate

# Start your Django project using Gunicorn
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
--bind 0.0.0.0:8000 \
--timeout=300 \
  --log-level=debug \
  --log-file=-

