# Deploy Workshop Pipeline on Server

Run these commands on your Ubuntu server:

```bash
cd /root/SEO-Agent
git pull origin main
./deploy_workshop_pipeline.sh
```

## What's New:

### 1. **Visual Pipeline Workshop** 
   - URL: `http://142.93.194.81:8000/workshop-pipeline`
   - See all 5 agents in a visual pipeline
   - Control each agent's output
   - Edit and approve at each step

### 2. **Live Data Integration**
   - Real Google search data via Jina/BrightData
   - Actual competitor analysis
   - Real market gaps and opportunities
   - Data flows through all agents

### 3. **Simple Interface**
   - Just enter service type (text input)
   - Enter location
   - Click "Start Pipeline"
   - Watch agents work with real data

### 4. **Full Control**
   - See what each agent produces
   - Edit outputs before proceeding
   - Approve or modify at each step
   - Save completed projects

## Architecture:

```
User Input → Data Gatherer → Market Scanner → SEO Strategist → Content Generator → Website Architect
    ↓             ↓              ↓                ↓                  ↓                    ↓
[Live Data]  [Competitors]  [Opportunities]  [Keywords]      [Content]          [Architecture]
    ↓             ↓              ↓                ↓                  ↓                    ↓
         [You Control Each Step - Edit/Approve Before Next Agent]
```

## Files Created:

1. **data_coordinator.py** - Manages live data flow
2. **workshop_pipeline.html** - Visual pipeline interface  
3. **workshop_pipeline_api.py** - API endpoints for pipeline
4. **Modified workshop_api.py** - Updated to use live data

This is the TRUE WORKSHOP you wanted - see and control everything!