#!/bin/bash
set -e

# Start arq worker in background
arq src.workers.WorkerSettings &

# Start Robyn web server in foreground
python -m src.main
