#!/bin/bash
SCRIPT_PATH="$(pwd)/run_user_monitor.sh"
CRON_FILE="/tmp/cron_gpu_monitor"
LOG_FILE="$(pwd)/gpu_log_cron.log"

echo "Setting up cron jobs for $SCRIPT_PATH"

# Get current crontab
crontab -l > "$CRON_FILE" 2>/dev/null

# Remove existing jobs for this script to avoid duplicates
sed -i "\|$SCRIPT_PATH|d" "$CRON_FILE"

# Add new jobs
# Daily collection at 23:55
echo "55 23 * * * $SCRIPT_PATH collect >> $LOG_FILE 2>&1" >> "$CRON_FILE"

# Weekly plot at 00:30 on Sunday
echo "30 0 * * 0 $SCRIPT_PATH weekly-plot >> $LOG_FILE 2>&1" >> "$CRON_FILE"

# Monthly archive at 01:00 on the 1st of the month
echo "0 1 1 * * $SCRIPT_PATH archive >> $LOG_FILE 2>&1" >> "$CRON_FILE"

# Install new crontab
crontab "$CRON_FILE"
rm "$CRON_FILE"

echo "Cron jobs installed successfully:"
crontab -l | grep "$SCRIPT_PATH"
