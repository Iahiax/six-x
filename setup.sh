#!/bin/bash
set -e

echo "=========================================================="
echo "   بدء تثبيت بنية CAPITAL-AI-X على سيرفر Linux...   "
echo "=========================================================="

sudo apt-get update && sudo apt-get install -y \
    python3-pip \
    python3-venv \
    tor \
    curl \
    git \
    sqlite3 \
    build-essential

sudo systemctl enable tor
sudo systemctl restart tor

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python3 -c "from state_persistence import SystemStateManager; SystemStateManager()"

if [ ! -f .env ]; then
    cp .env.example .env
fi

echo "=========================================================="
echo "   اكتمل التثبيت بنجاح! يمكنك الآن تشغيل main.py   "
echo "=========================================================="
