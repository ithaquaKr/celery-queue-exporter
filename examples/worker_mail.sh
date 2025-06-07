#!/bin/bash

celery -A app.celery worker -n worker_mail --loglevel=info -Q mail
