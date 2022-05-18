#! /bin/bash

mkdir ./env

# Copy files
cp .env.cookiecutter ./env/.env.dev
sed -i 's/ENVIRONMENT="TEST"/ENVIRONMENT="DEV"/g' ./env/.env.dev
cp .env.cookiecutter ./env/.env.test
cp .env.cookiecutter ./env/.env.prod
sed -i 's/ENVIRONMENT="TEST"/ENVIRONMENT="PROD"/g' ./env/.env.prod

# Execute mode
chmod -R +x ./env
# Delete cookiecutter
rm -f .env.cookiecutter
