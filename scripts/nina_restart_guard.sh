#!/bin/bash
# nina_restart_guard.sh
# Called by cron every 5 minutes as a belt-and-suspenders guard.
# If nina.service is inactive/failed, restart it.
# Crontab: */5 * * * * /bin/bash ~/nina/scripts/nina_restart_guard.sh >> ~/nina/runtime/logs/restart_guard.log 2>&1

SERVICE="nina.service"
LOG_FILE="$HOME/nina/runtime/logs/restart_guard.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

STATUS=$(systemctl --user is-active "$SERVICE" 2>/dev/null)

if [ "$STATUS" != "active" ]; then
    echo "[$TIMESTAMP] $SERVICE is '$STATUS' — restarting..."
    systemctl --user restart "$SERVICE"
    sleep 5
    NEW_STATUS=$(systemctl --user is-active "$SERVICE" 2>/dev/null)
    echo "[$TIMESTAMP] After restart: $NEW_STATUS"
else
    echo "[$TIMESTAMP] $SERVICE is active. OK."
fi
