#!/bin/bash

# Git Repository Status Check for IntelAI
# Verifies git status, branch, and commit history for presentation readiness

echo "=========================================="
echo "IntelAI Git Repository Status Check"
echo "=========================================="
echo ""

cd IntelAI || { echo "IntelAI directory not found"; exit 1; }

echo "Current Branch:"
git branch --show-current
echo ""

echo "Git Status (uncommitted changes):"
if git status --porcelain | grep -q .; then
    echo "⚠ Uncommitted changes found:"
    git status --short
else
    echo "✓ Working directory clean"
fi
echo ""

echo "Recent Commits (last 5):"
git log --oneline -5
echo ""

echo "Remote Status:"
git remote -v
echo ""

echo "Branch Sync Status:"
UPSTREAM_STATUS="no-upstream"
if git rev-parse @{u} >/dev/null 2>&1; then
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u})
    if [ "$LOCAL" = "$REMOTE" ]; then
        echo "✓ Local branch matches remote"
        UPSTREAM_STATUS="synced"
    else
        echo "⚠ Local and remote differ"
        echo "Local: $LOCAL"
        echo "Remote: $REMOTE"
        UPSTREAM_STATUS="out-of-sync"
    fi
else
    echo "⚠ No upstream branch configured"
fi
echo ""

echo "AI Co-Author Check:"
if git log --all --oneline | grep -iE 'co-authored-by.*claude|co-authored-by.*gpt|co-authored-by.*ai|co-authored-by.*anthropic' > /dev/null; then
    echo "❌ FOUND AI co-authors in commit history"
    git log --all --oneline | grep -iE 'co-authored-by.*claude|co-authored-by.*gpt|co-authored-by.*ai|co-authored-by.*anthropic'
else
    echo "✓ No AI co-authors found in commit history"
fi
echo ""

echo "Commit Author Check:"
echo "Checking for non-Yacine-ai-tech authors..."
NON_YACINE=$(git log --all --format='%an' | sort -u | grep -v 'Yacine-ai-tech' | grep -v '^$' || echo "")
if [ -n "$NON_YACINE" ]; then
    echo "❌ Found non-Yacine-ai-tech authors:"
    echo "$NON_YACINE"
else
    echo "✓ All commits are by Yacine-ai-tech"
fi
echo ""

echo "=========================================="
echo "Git Status Summary"
echo "=========================================="
echo "Repository: IntelAI"
echo "Current Branch: $(git branch --show-current)"
echo "Working Directory: $(git status --porcelain | grep -q . && echo 'dirty' || echo 'clean')"
echo "Remote Sync: $UPSTREAM_STATUS"

if git log --all --oneline | grep -iE 'co-authored-by.*claude|co-authored-by.*gpt|co-authored-by.*ai' > /dev/null; then
    echo "AI Co-Authors: FOUND"
else
    echo "AI Co-Authors: none"
fi
echo ""