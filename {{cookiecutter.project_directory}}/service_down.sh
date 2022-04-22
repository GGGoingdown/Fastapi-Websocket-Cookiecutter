#! /bin/bash

# Shutdown
docker-compose -f docker-compose-dev.yml --env-file ./env/.env.dev down -v
