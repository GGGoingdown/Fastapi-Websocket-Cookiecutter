#! /bin/bash

# Link DB
python ./app/pre_start.py

# Create schema
aerich upgrade

# Initial data
python ./app/initial/initial_data.py


if [[ "${ENVIRONMENT}" == "PROD" ]]; then
    echo "Production Mode"
    uvicorn app.main:app --host=0.0.0.0 --port=8000 --no-access-log
else
    echo "${ENVIRONMENT} Mode"
    uvicorn app.main:app --host=0.0.0.0 --port=8000 --reload
fi
