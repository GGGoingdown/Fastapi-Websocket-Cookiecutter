#! /bin/bash

set -e

set -x


# Link DB
python ./app/pre_start.py

# Create schema
aerich upgrade


# Initial data
python ./tests/initial_test_data.py


# Pytest
pytest -p no:warnings
