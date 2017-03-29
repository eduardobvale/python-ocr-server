#!/bin/sh

sleep 10

celery worker -l info -A app.celery
