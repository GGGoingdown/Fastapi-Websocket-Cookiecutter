#! /bin/bash

mkdir ./env

# Copy files
cp .env.cookiecutter ./env/.env.dev
cp .env.cookiecutter ./env/.env.test
cp .env.cookiecutter ./env/.env.prod

# Execute mode
chmod -R +x ./env
# Delete cookiecutter
rm -f .env.cookiecutter
