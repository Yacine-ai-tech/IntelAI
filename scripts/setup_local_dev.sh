#!/usr/bin/env bash
set -euo pipefail

# OmniIntelOS local dev setup script for WSL (Ubuntu 22.04)
# - Installs system packages needed for the project
# - Ensures PostgreSQL service is running and creates a role/db matching the Linux user
# - Creates a Python venv at .venv and installs CPU-only PyTorch + requirements
# - Runs npm ci in frontend if present

# Run this script from the project root: ./scripts/setup_local_dev.sh
# You will be prompted for your sudo password.

PKGS=( 
  build-essential python3-venv python3-dev libpq-dev git curl pkg-config 
  libjpeg-dev zlib1g-dev libpoppler-cpp-dev poppler-utils tesseract-ocr ffmpeg 
)

echo "Updating apt and installing system packages (requires sudo)..."
sudo apt update
sudo apt install -y "${PKGS[@]}"

echo "Ensuring PostgreSQL service is started..."
sudo service postgresql start || true

CURRENT_USER=$(whoami)
# create a role and DB with the current user's name (no-op if exist)
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$CURRENT_USER'" | grep -q 1; then
  echo "Postgres role '$CURRENT_USER' already exists"
else
  echo "Creating postgres role '$CURRENT_USER'"
  sudo -u postgres createuser --no-createdb --no-createrole --no-superuser "$CURRENT_USER" || true
fi

if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$CURRENT_USER"; then
  echo "Postgres DB '$CURRENT_USER' already exists"
else
  echo "Creating postgres DB '$CURRENT_USER' owned by '$CURRENT_USER'"
  sudo -u postgres createdb -O "$CURRENT_USER" "$CURRENT_USER" || true
fi

# Create Python venv
if [ -d ".venv" ]; then
  echo ".venv already exists, skipping venv creation"
else
  echo "Creating Python virtualenv at .venv"
  python3 -m venv .venv
fi

echo "Upgrading pip, wheel and setuptools in venv"
.venv/bin/pip install --upgrade pip setuptools wheel

# Install CPU-only torch first to avoid unintended CUDA wheels
echo "Installing CPU-only PyTorch wheel (torch==2.3.1+cpu)"
.venv/bin/pip install --index-url https://download.pytorch.org/whl/cpu torch==2.3.1+cpu

# Install project requirements
if [ -f requirements.txt ]; then
  echo "Installing Python requirements from requirements.txt (this can take a while)"
  .venv/bin/pip install --prefer-binary -r requirements.txt
else
  echo "No requirements.txt found in project root"
fi

# Frontend install
if [ -f frontend/package.json ]; then
  echo "Installing frontend dependencies (npm ci)"
  (cd frontend && npm ci)
else
  echo "No frontend found at ./frontend"
fi

echo "Setup script finished. Activate the venv with: source .venv/bin/activate"

echo "Notes:"
echo " - This script installs many system libs (poppler, tesseract, ffmpeg, build-essential, libpq-dev) to support PDF/ocr/tts/whisper builds."
echo " - If you prefer not to install some system packages, edit this script accordingly."

echo "If you run this and paste the output here I will verify success and run any remaining steps."