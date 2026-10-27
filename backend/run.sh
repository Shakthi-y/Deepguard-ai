#!/usr/bin/env bash
set -e

# DeepGuard AI - backend launcher
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo "No .env found — copying .env.example to .env"
    cp .env.example .env
fi

echo "Starting DeepGuard AI backend on http://localhost:8000 ..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
