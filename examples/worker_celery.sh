#!/bin/bash

celery -A app.celery worker -n worker_celery --loglevel=info -Q celery
