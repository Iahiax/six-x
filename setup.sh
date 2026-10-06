#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo " Capital-AI-X Setup Script"
echo "========================================"
echo ""

echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

if [ -f requirements.txt ]; then
  echo "📥 Installing dependencies..."
  python3 -m pip install -r requirements.txt --quiet
  echo "✅ Dependencies installed"
else
  echo "❌ requirements.txt not found" >&2
  exit 1
fi

if [ ! -f .env ] && [ -f .env.example ]; then
  echo "📝 Creating .env from .env.example..."
  cp .env.example .env
  echo "✅ Created .env (edit this file with your credentials)"
fi

mkdir -p logs
echo "📁 Created logs directory"

echo ""
echo "========================================"
echo "✅ Setup completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your credentials"
echo "  2. Run: python main.py"
echo "  3. Or run: streamlit run app.py"
echo "  4. Or run: docker-compose up --build"
echo ""
echo "Default trading mode: DEMO (safe)"
echo "To switch to LIVE: Use /mode command in Telegram Bot"
echo ""
