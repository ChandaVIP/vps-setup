#!/bin/bash

/usr/sbin/sshd

PORT="${PORT:-8080}"

echo "Starting Websockify on port $PORT forwarding to SSH port 22..."
exec websockify 0.0.0.0:$PORT localhost:22
