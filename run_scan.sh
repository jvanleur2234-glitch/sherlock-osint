#!/bin/bash
# Sherlock Scanner Wrapper
# Usage: ./run_scan.sh <job_id> <username> <output_dir>

JOB_ID="$1"
USERNAME="$2"
OUT_DIR="$3"
LOG_FILE="${OUT_DIR}/scan.log"

mkdir -p "$OUT_DIR"

# Run maigret with txt + csv output, log everything
maigret "$USERNAME" \
  -T \
  -C \
  --folderoutput "$OUT_DIR" \
  >> "$LOG_FILE" 2>&1

# Touch done file when complete
touch "${OUT_DIR}/done"
