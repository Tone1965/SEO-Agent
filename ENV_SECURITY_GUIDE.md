# 🔒 Environment File Security Guide

## Current Protection Status ✅

Your `.env` files are now protected with multiple layers of security:

1. **Read-only permissions** - Files cannot be accidentally overwritten
2. **Timestamped backups** - Created automatically
3. **Secure off-project backup** - Stored in `~/.seo-agent-secrets/`
4. **Git ignored** - Will never be committed to version control

## Your API Keys Locations

### Primary Files:
- `/mnt/c/Users/kimma/SEO-Agent/.env`
- `/mnt/c/Users/kimma/SEO-Agent/ranksavvy-graphql/.env`

### Backup Locations:
- `/mnt/c/Users/kimma/SEO-Agent/.env.backup`
- `/mnt/c/Users/kimma/SEO-Agent/.env.backup_[timestamp]`
- `~/.seo-agent-secrets/.env.secure` (most secure)

## Security Best Practices

### 1. **Never Share Screenshots of .env Files**
Your API keys are sensitive - treat them like passwords.

### 2. **Use Read-Only Mode**
Keep files in read-only mode when not editing:
```bash
chmod 444 .env
```

### 3. **Edit Safely**
When you need to edit:
```bash
# Make writable
chmod 644 .env

# Edit the file
nano .env

# Make read-only again
chmod 444 .env
```

### 4. **Regular Backups**
Create timestamped backups before major changes:
```bash
cp .env .env.backup_$(date +%Y%m%d_%H%M%S)
```

### 5. **Check Git Status**
Always verify .env is not staged:
```bash
git status
# .env should NEVER appear in staged files
```

## Recovery Commands

### Restore from secure backup:
```bash
cp ~/.seo-agent-secrets/.env.secure .env
```

### Restore from timestamped backup:
```bash
ls -la .env.backup_*  # List all backups
cp .env.backup_20250703_* .env  # Choose specific backup
```

### Check current permissions:
```bash
ls -la .env*
```

## Prevent Future Accidents

### 1. **Add Pre-edit Check**
Create this alias in your `.bashrc`:
```bash
alias edit-env='echo "⚠️  About to edit sensitive file. Create backup? (y/n)" && read -r response && [ "$response" = "y" ] && cp .env .env.backup_$(date +%Y%m%d_%H%M%S) && chmod 644 .env && nano .env && chmod 444 .env'
```

### 2. **Use Environment-Specific Files**
- `.env` - Production keys
- `.env.local` - Local development
- `.env.example` - Template only (no real keys)

### 3. **Script Safety**
Always use the `--no-clobber` or `-n` flag with cp:
```bash
cp -n .env.example .env  # Won't overwrite if .env exists
```

## Emergency Contacts

If keys are compromised:
1. **Jina.ai** - Regenerate at https://jina.ai/dashboard
2. **Anthropic** - Regenerate at https://console.anthropic.com
3. **OpenAI** - Regenerate at https://platform.openai.com

## Your Current Keys (Encrypted Reference)

Keys are safely stored in:
- Primary: `.env` files (read-only)
- Backup: `~/.seo-agent-secrets/.env.secure` (hidden, secure)
- Never store in: Code files, logs, or version control

---

**Remember**: These API keys are like credit cards - protect them carefully! 🔐