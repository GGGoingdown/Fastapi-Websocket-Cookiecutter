#! /bin/bash

# Link DB
python ./app/pre_start.py

# Create schema
aerich upgrade

# Initial data
python ./app/initial/initial_data.py


if [[ "${ENVIRONMENT}" == "PROD" ]]; then
    echo "Production Mode"
    celery -A app.main.celery worker --concurrency=1 --loglevel=error
else
    echo "${ENVIRONMENT} Mode"
    python ./app/main.py
fi
