#!/bin/bash

## Start Nginx
nginx

## Start Gunicorn
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:8000
