#! /bin/bash

set -e
set -x

# Remove old project if exist
rm -rf ./Testing-Project
# Cookiecutter create project
#! Note: Project name can not change, Must modify .drone.yml file if change this
cookiecutter --no-input -f ./ project_name="Testing Project"
# Change to Testing Project
#! Note: This can not change
cd ./Testing-Project

poetry install

bash ./script/start_test.sh
