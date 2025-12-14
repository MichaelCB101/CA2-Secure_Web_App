#!/bin/bash
set -e
#this code is a script that runs the create_users script and fuzzing script automatically when the container is run.
#The true means that the container and app will run even if the script can not run. the app is also run here
echo "Running user creation script"
python create_users.py || true

echo "Running fuzzing script"
python fuzzing_login_and_register_pages.py || true

echo "Starting Flask app"
exec python app.py
