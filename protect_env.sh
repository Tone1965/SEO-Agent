#!/bin/bash

# Protect .env files from accidental modification
echo "🔒 Securing .env files..."

# 1. Create backups with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp .env .env.backup_${TIMESTAMP} 2>/dev/null
cp ranksavvy-graphql/.env ranksavvy-graphql/.env.backup_${TIMESTAMP} 2>/dev/null

# 2. Set read-only permissions (on WSL/Linux)
chmod 444 .env .env.backup* 2>/dev/null
chmod 444 ranksavvy-graphql/.env ranksavvy-graphql/.env.backup* 2>/dev/null

# 3. Add to .gitignore if not already there
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
fi
if ! grep -q "^\.env\.backup" .gitignore 2>/dev/null; then
    echo ".env.backup*" >> .gitignore
fi
if ! grep -q "^\.env\.local" .gitignore 2>/dev/null; then
    echo ".env.local" >> .gitignore
fi

# 4. Create a secure copy in user home (outside project)
mkdir -p ~/.seo-agent-secrets
cp .env ~/.seo-agent-secrets/.env.secure
chmod 600 ~/.seo-agent-secrets/.env.secure

echo "✅ Protection applied:"
echo "   - Backups created with timestamp"
echo "   - Files set to read-only"
echo "   - Added to .gitignore"
echo "   - Secure copy saved to ~/.seo-agent-secrets/"
echo ""
echo "To edit .env files in the future:"
echo "   chmod 644 .env"
echo "   # make your edits"
echo "   chmod 444 .env"
echo ""
echo "To restore from backup:"
echo "   cp ~/.seo-agent-secrets/.env.secure .env"