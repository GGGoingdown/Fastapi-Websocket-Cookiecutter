#! /bin/bash

set -e



# Build
docker-compose -f docker-compose-test.yml --env-file ./env/.env.test build --build-arg ENVIRONMENT=test
# Start
docker-compose -f docker-compose-test.yml --env-file ./env/.env.test up -d
# Show test log
docker logs -f cookiecutterproject_directory_app_1
# Shutdown
docker-compose -f docker-compose-test.yml --env-file ./env/.env.test down -v
