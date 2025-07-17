#!/bin/bash

export REDIS_USE_SENTINEL=true
export REDIS_SENTINEL_HOSTS=localhost:26379,localhost:26380,localhost:26381
export REDIS_SENTINEL_MASTER_NAME=mymaster

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
