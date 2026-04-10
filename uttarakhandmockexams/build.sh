#!/bin/bash
# Render Build Script — UttarakhandMockExams
echo "=== UttarakhandMockExams Build ==="

# Copy frontend to static folder so server can serve it
mkdir -p static
cp frontend.html static/index.html
echo "Frontend copied to static/index.html"

# Seed database only if it doesn't exist
if [ ! -f "$DB_PATH" ] && [ ! -f "uttarakhandmockexams.db" ]; then
    echo "Seeding database with 7200 questions..."
    python3 seed.py
    echo "Database seeded successfully"
else
    echo "Database already exists, skipping seed"
fi

echo "Build complete!"
