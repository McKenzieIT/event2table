#!/bin/bash
# LaunchAgent wrapper for update-docs task
# This wrapper handles macOS security restrictions

SCRIPT_DIR="/Users/mckenzie/Documents/event2table/scripts/scheduled"
LOG_FILE="/Users/mckenzie/Documents/event2table/logs/launcher.log"

# Change to project directory first
cd "/Users/mckenzie/Documents/event2table" || exit 1

# Now execute the main script
exec "$SCRIPT_DIR/update-docs-scheduled.sh"
