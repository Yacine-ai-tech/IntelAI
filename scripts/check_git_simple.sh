#!/bin/bash

# Simple Git Repository Status Check for IntelAI
echo "=========================================="
echo "IntelAI Git Repository Status Check"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.." || { echo "IntelAI directory not found"; exit 1; }

echo "Current Branch:"
git branch --show-current
echo ""

echo "Git Status:"
git status --short
echo ""

echo "Recent Commits (last 5):"
git log --oneline -5
echo ""

echo "Remote Configuration:"
git remote -v
echo ""

echo "AI Co-Author Check:"
AI_CO_AUTHORS=$(git log --all --oneline | grep -iE 'co-authored-by.*claude|co-authored-by.*gpt|co-authored-by.*ai|co-authored-by.*anthropic' || echo "")
if [ -n "$AI_CO_AUTHORS" ]; then
    echo "❌ FOUND AI co-authors:"
    echo "$AI_CO_AUTHORS"
else
    echo "✓ No AI co-authors found"
fi
echo ""

echo "Commit Author Check:"
ALL_AUTHORS=$(git log --all --format='%an' | sort -u)
NON_YACINE=$(echo "$ALL_AUTHORS" | grep -v 'Yacine-ai-tech' | grep -v '^$' || echo "")
if [ -n "$NON_YACINE" ]; then
    echo "❌ Found non-Yacine-ai-tech authors:"
    echo "$NON_YACINE"
else
    echo "✓ All commits are by Yacine-ai-tech"
fi
echo ""

echo "=========================================="
echo "Quick Summary"
echo "=========================================="
echo "Branch: $(git branch --show-current)"
echo "Working dir: $(git status --porcelain | grep -q . && echo 'dirty' || echo 'clean')"
echo "AI co-authors: $([ -n "$AI_CO_AUTHORS" ] && echo 'FOUND' || echo 'none')"
echo "Non-Yacine authors: $([ -n "$NON_YACINE" ] && echo 'FOUND' || echo 'none')"
echo ""