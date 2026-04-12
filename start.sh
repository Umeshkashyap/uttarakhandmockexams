#!/bin/bash
cd "$(dirname "$0")/backend"
if [ ! -f ume_final.db ]; then
    python3 seed.py
fi
echo "Server: http://localhost:5000"
python3 server.py