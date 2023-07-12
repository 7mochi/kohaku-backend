#!/usr/bin/env bash
set -euo pipefail

if [ -z "$APP_ENV" ]; then
  echo "Please set APP_ENV"
  exit 1
fi

if [ "$APP_ENV" == "local" ]; then
  EXTRA_ARGUMENTS="--reload"
else
  EXTRA_ARGUMENTS=""
fi

cd app
export PYTHONPATH=$PWD

exec uvicorn web_api:app \
  --host "$APP_HOST" \
  --port "$APP_PORT" \
  $EXTRA_ARGUMENTS
