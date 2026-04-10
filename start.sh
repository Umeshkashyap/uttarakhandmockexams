#!/bin/bash
clear
echo "======================================================"
echo "  UttarakhandMockExams v3 - Light Theme"
echo "  No Login Required | AdSense Ready"
echo "======================================================"
echo ""
cd "$(dirname "$0")/backend"
if [ ! -f uttarakhandmockexams.db ]; then
    echo "  Seeding 7200 questions..."
    python3 seed.py
    echo ""
fi
echo "  Server: http://localhost:5000"
echo "  Admin:  admin@uttarakhandmockexams.in / admin123"
echo ""
python3 server.py
