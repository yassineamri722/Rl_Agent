#!/bin/bash
gunicorn -k uvicorn.workers.UvicornWorker -w 1 -b 0.0.0.0:8000 main:app
