#!/bin/bash
set -e
echo "Building UttarakhandMockExams..."
mkdir -p static uploads
cp frontend.html static/index.html
echo "Running seed..."
python3 seed.py
echo "Build complete!"
