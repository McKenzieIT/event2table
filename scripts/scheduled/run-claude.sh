#!/bin/bash
# Wrapper script to run Claude CLI with proper environment

# Set PATH
export PATH="/Users/mckenzie/.nvm/versions/node/v20.20.0/bin:/usr/local/bin:/usr/bin:/bin"

# Set NODE_PATH if needed
export NODE_PATH="/Users/mckenzie/.nvm/versions/node/v20.20.0/lib/node_modules"

# Change to project directory
cd /Users/mckenzie/Documents/event2table

# Run Claude CLI with the provided arguments
exec /Users/mckenzie/.nvm/versions/node/v20.20.0/bin/claude "$@"
