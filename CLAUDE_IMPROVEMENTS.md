# Suggested Improvements to CLAUDE.md

## 1. Add Docker-Specific Commands

Add after the "Development Commands" section:

```bash
## Docker Development Commands

# Build and run with Docker Compose
docker-compose build --no-cache    # Rebuild all images
docker-compose up -d               # Start all services
docker-compose logs -f seo-agent   # View application logs
docker-compose ps                  # Check service status
docker-compose down -v             # Stop and remove volumes

# Debug Docker issues
docker exec -it seo-agent-seo-agent-1 bash  # Shell into container
docker exec seo-agent-seo-agent-1 pip list  # Check installed packages
```

## 2. Add Workshop Mode Documentation

Add new section after "API Endpoints":

```markdown
## Workshop Mode

### Accessing Workshop Interface
- **URL**: `/workshop` or `/workshop.html`
- **Purpose**: Manual control over individual AI agents
- **Features**: Step-by-step execution, output preview, approval workflow

### Workshop API Endpoints
- `POST /api/run-agent` - Execute single agent
- `POST /api/save-workflow` - Save workflow state
- `GET /api/load-workflow/<id>` - Load saved workflow
- `GET /api/agent-config/<agent_id>` - Get agent configuration options
```

## 3. Add Production Deployment Section

Add after "Deployment Guidelines":

```markdown
## Production Deployment (Digital Ocean)

### Quick Deploy Commands
```bash
# On server (142.93.194.81)
cd /root/SEO-Agent
git pull
docker-compose down
docker-compose build --no-cache seo-agent
docker-compose up -d
```

### Common Production Issues
1. **502 Bad Gateway**: Check if containers are running with `docker-compose ps`
2. **Memory Issues**: Monitor with `docker stats`
3. **Disk Space**: Check with `df -h`, clean with `docker system prune -a`
```

## 4. Add Specific File Warnings

Add to "Important Notes" section:

```markdown
### Critical Files - Handle with Care
- **requirements.txt**: Changes require Docker rebuild
- **docker-compose.yml**: Affects all services
- **nginx.conf**: Can break site accessibility
- **.env files**: Never commit, contains secrets
```

## 5. Add Quick Troubleshooting Flowchart

```markdown
## Quick Troubleshooting Guide

Site not loading?
├─ Check containers: `docker-compose ps`
├─ If not running: `docker-compose up -d`
├─ If 502 error: Check logs `docker-compose logs seo-agent`
└─ If build fails: Check requirements.txt versions

API not responding?
├─ Check Flask logs: `docker-compose logs seo-agent | grep ERROR`
├─ Check Redis: `docker-compose logs redis`
└─ Verify API keys in .env file
```

## 6. Add Testing Commands That Actually Exist

Replace the pytest references with:

```bash
# Test system components
python -c "from main import AIClient; client = AIClient(); print('AI Client OK')"
python -c "import redis; r = redis.from_url('redis://localhost:6379'); r.ping(); print('Redis OK')"
python -c "from website_generator import WebsiteFileGenerator; print('Generator OK')"

# Test API endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/status/test
```

## 7. Add Memory/Performance Limits

```markdown
## Resource Considerations

### Memory Requirements
- Development: 4GB RAM minimum
- Production: 8GB RAM recommended
- Each agent uses ~500MB during execution
- Concurrent generations multiply memory usage

### API Rate Limits
- Claude: 40,000 tokens/minute
- OpenAI: 90,000 tokens/minute
- Plan for ~10,000 tokens per website
```

These improvements would make CLAUDE.md more practical for day-to-day development and troubleshooting.