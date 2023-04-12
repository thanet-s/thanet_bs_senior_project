#!/bin/bash

exec gunicorn -w $(( $(grep -c processor /proc/cpuinfo) * 2)) -b :8000 --forwarded-allow-ips="*" --worker-tmp-dir /dev/shm --timeout 60 --log-file=- --access-logfile=- -k uvicorn.workers.UvicornWorker main:app