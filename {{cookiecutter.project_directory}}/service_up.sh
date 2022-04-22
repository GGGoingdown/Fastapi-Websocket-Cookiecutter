#! /bin/bash


# Build
docker-compose -f docker-compose-dev.yml --env-file ./env/.env.dev build --build-arg ENVIRONMENT=dev
# Start
docker-compose -f docker-compose-dev.yml --env-file ./env/.env.dev up -d
