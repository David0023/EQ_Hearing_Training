#!/bin/sh

status=0
docker compose --profile test run --build --rm test || status=$?
docker compose --profile test stop db-test || true
exit "$status"
