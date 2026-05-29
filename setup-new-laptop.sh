#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# setup-new-laptop.sh
#
# Run this script ONCE on the new machine to reconstruct the full workspace.
#
# What it does:
#   1. Clones all 6 private repos from GitHub (code only, ~8.9 MB total)
#   2. Creates a Python 3.10 venv in each project
#   3. Installs deps (reads from pip cache if you've already synced it — see
#      the transfer instructions at the top of this file)
#   4. Copies .env.example → .env so you can fill in your keys
#
# Prerequisites on new machine:
#   - git configured with your GitHub credentials (HTTPS or SSH)
#   - Python 3.10 installed  (sudo apt install python3.10 python3.10-venv)
#   - libpq-dev, build-essential, gcc (for psycopg binary wheels)
#     sudo apt install -y libpq-dev build-essential gcc
#
# BEFORE running this script, optionally sync the pip cache from the old
# machine to avoid re-downloading ~4 GB of packages:
#
#   On OLD machine (replace NEW_IP with your new laptop's IP):
#     rsync -av --progress ~/.cache/pip/ user@NEW_IP:~/.cache/pip/
#
#   If both machines are on LAN this takes 1-3 minutes instead of
#   30-60 minutes downloading fresh.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

GITHUB_USER="Yacine-ai-tech"
WORKSPACE="$HOME/projects/credential"
PYTHON="${PYTHON:-python3.10}"

REPOS=(OmniIntelOS AgentKit DocIntel RAGeval VoiceFlow StreamPulse)

echo "════════════════════════════════════════════"
echo " Credential workspace setup"
echo " Target: $WORKSPACE"
echo " Python: $($PYTHON --version 2>&1)"
echo "════════════════════════════════════════════"
echo ""

mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

# ── Step 1: Clone repos ───────────────────────────────────────────────────────
echo "── Step 1: Cloning repos from github.com/$GITHUB_USER ──"
for repo in "${REPOS[@]}"; do
    if [ -d "$repo/.git" ]; then
        echo "  $repo: already cloned, pulling latest..."
        git -C "$repo" pull --ff-only origin master 2>&1 | tail -1
    else
        echo "  $repo: cloning..."
        git clone "https://github.com/$GITHUB_USER/$repo.git"
    fi
    # Ensure develop branch is tracked
    git -C "$repo" fetch --quiet origin develop 2>/dev/null || true
    git -C "$repo" checkout -B develop --track origin/develop 2>/dev/null || true
    git -C "$repo" checkout master 2>/dev/null || true
done
echo ""

# ── Step 2: Create venvs and install deps ────────────────────────────────────
echo "── Step 2: Creating venvs and installing dependencies ──"
for repo in "${REPOS[@]}"; do
    echo ""
    echo "  [$repo]"
    cd "$WORKSPACE/$repo"

    if [ ! -d ".venv" ]; then
        echo "    creating venv..."
        $PYTHON -m venv .venv
    else
        echo "    venv already exists"
    fi

    source .venv/bin/activate

    echo "    upgrading pip..."
    pip install -q -U pip wheel setuptools

    echo "    installing requirements.txt..."
    pip install -q -r requirements.txt

    deactivate
    echo "    done: $($WORKSPACE/$repo/.venv/bin/python -c 'import sys; print(sys.version.split()[0])')"
    cd "$WORKSPACE"
done
echo ""

# ── Step 3: Copy .env.example → .env ─────────────────────────────────────────
echo "── Step 3: Setting up .env files ──"
for repo in "${REPOS[@]}"; do
    if [ ! -f "$WORKSPACE/$repo/.env" ] && [ -f "$WORKSPACE/$repo/.env.example" ]; then
        cp "$WORKSPACE/$repo/.env.example" "$WORKSPACE/$repo/.env"
        echo "  $repo: .env created from .env.example — fill in your API keys"
    else
        echo "  $repo: .env already exists"
    fi
done
echo ""

# ── Step 4: Verify smoke tests pass ──────────────────────────────────────────
echo "── Step 4: Smoke test verification ──"
echo "  (skipping heavy projects with large model downloads on first run)"
for repo in DocIntel VoiceFlow StreamPulse; do
    echo -n "  $repo: "
    result=$(cd "$WORKSPACE/$repo" && \
        timeout 120 .venv/bin/python -m pytest tests/ -q --no-header \
        -p no:cacheprovider 2>&1 | tail -1)
    echo "$result"
done
echo ""

echo "════════════════════════════════════════════"
echo " Setup complete."
echo ""
echo " Next steps:"
echo "   1. Fill in API keys in each project's .env file:"
for repo in "${REPOS[@]}"; do
    echo "        \$EDITOR $WORKSPACE/$repo/.env"
done
echo ""
echo "   2. For OmniIntelOS frontend:"
echo "        cd $WORKSPACE/OmniIntelOS/frontend && npm install"
echo ""
echo "   3. Verify AgentKit/RAGeval (they download ML models on first run):"
echo "        cd $WORKSPACE/AgentKit && .venv/bin/python -m pytest tests/ -q"
echo "        cd $WORKSPACE/RAGeval  && .venv/bin/python -m pytest tests/ -q"
echo ""
echo "   4. Start any project:"
echo "        cd $WORKSPACE/DocIntel && source .venv/bin/activate"
echo "        uvicorn api:app --port 8001 --reload"
echo "════════════════════════════════════════════"
