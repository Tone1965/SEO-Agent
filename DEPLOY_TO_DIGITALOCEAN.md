# Deploy to DigitalOcean

## Quick Deploy Commands

SSH into your server and run:

```bash
ssh root@142.93.194.81

# Navigate to project
cd /root/SEO-Agent

# Pull the new branch with all changes
git fetch origin
git checkout workshop-pipeline-rebuild
git pull origin workshop-pipeline-rebuild

# Make deploy script executable and run it
chmod +x deploy_workshop_pipeline.sh
./deploy_workshop_pipeline.sh
```

## What This Deploys

✅ **Complete Workshop Pipeline** with:
- Visual pipeline showing all 5 agents connected
- Live Google data from Jina/BrightData  
- User control: edit/approve each agent's output
- Real-time status monitoring
- Simple inputs (just service type + location)

## Access URLs

After deployment, access at:
- **Main Workshop**: http://142.93.194.81:8000/workshop-pipeline

## Files Deployed

- `workshop_pipeline_api.py` - New API with live data integration
- `data_coordinator.py` - Manages live data flow to agents  
- `frontend/workshop_pipeline.html` - Complete pipeline interface
- `deploy_workshop_pipeline.sh` - Deployment script

## Branch Info

- **Branch**: `workshop-pipeline-rebuild`
- **Changes**: All 10 agents modified for live data, visual pipeline, user controls