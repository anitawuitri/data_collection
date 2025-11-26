#!/bin/bash

# Create user with same ID as host user
if [ ! -z "$USER_ID" ] && [ ! -z "$GROUP_ID" ]; then
    groupadd -g "$GROUP_ID" -o user
    useradd -m -u "$USER_ID" -g "$GROUP_ID" -o -s /bin/bash user
    export HOME=/home/user
    
    # Execute command as user
    exec gosu user "$@"
else
    # Fallback to root execution if no ID provided
    exec "$@"
fi
