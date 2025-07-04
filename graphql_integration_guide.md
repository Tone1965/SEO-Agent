# RankSavvyGraphQL Integration Guide

## Setting Up the MCP Server

To create the RankSavvyGraphQL MCP server, run:

```bash
npx @anthropic-ai/create-mcp-server@latest ranksavvy-graphql
```

## Frontend Integration with GraphQL

### 1. Add GraphQL Client to Frontend

Add this to your `frontend/index.html` in the `<head>` section:

```html
<!-- GraphQL Client -->
<script src="https://cdn.jsdelivr.net/npm/graphql-request@6/dist/index.min.js"></script>
```

### 2. Update JavaScript to Use GraphQL

Replace the existing REST API calls with GraphQL queries:

```javascript
// GraphQL endpoint
const GRAPHQL_ENDPOINT = '/api/graphql';

// Create GraphQL client
const graphQLClient = new GraphQLRequest.GraphQLClient(GRAPHQL_ENDPOINT, {
    headers: {
        'Content-Type': 'application/json',
    }
});

// Example: Market Scan Query
async performMarketScan() {
    if (!this.marketSearchQuery) {
        alert('Please enter a business name, competitor, or market keyword');
        return;
    }
    
    this.isScanning = true;
    this.marketScanResults = null;
    
    try {
        const query = `
            query PerformSEOSearch($query: String!, $platforms: [SearchPlatform!]) {
                seoSearch(query: $query, platforms: $platforms) {
                    totalResults
                    executionTime
                    results {
                        platform
                        success
                        error
                        data {
                            title
                            url
                            snippet
                            position
                        }
                    }
                }
            }
        `;
        
        const variables = {
            query: this.marketSearchQuery,
            platforms: ['GOOGLE', 'BING', 'YOUTUBE', 'REDDIT']
        };
        
        const data = await graphQLClient.request(query, variables);
        
        if (data.seoSearch) {
            // Process results into market scan format
            this.marketScanResults = {
                competitorCount: data.seoSearch.totalResults,
                platformCount: data.seoSearch.results.filter(r => r.success).length,
                opportunityScore: Math.min(100, 100 - (data.seoSearch.totalResults * 2)),
                presence: data.seoSearch.results.map(result => ({
                    query: result.platform,
                    results: result.data || []
                })),
                raw_data: data.seoSearch
            };
        }
    } catch (error) {
        alert('Market scan failed: ' + error.message);
    } finally {
        this.isScanning = false;
    }
}

// Example: Generate Website with GraphQL
async generateWebsite() {
    if (!this.formData.businessType || !this.formData.location) {
        alert('Please fill in all required fields');
        return;
    }

    this.isGenerating = true;
    this.progress = 0;
    
    try {
        const mutation = `
            mutation GenerateWebsite($input: GenerateWebsiteInput!) {
                generateWebsite(input: $input) {
                    id
                    businessType
                    location
                    status
                    progress
                    agentResults
                    websiteFiles
                    createdAt
                }
            }
        `;
        
        const variables = {
            input: {
                businessType: this.formData.businessType,
                location: this.formData.location,
                targetKeywords: this.formData.keywords.split(',').map(k => k.trim()),
                competitorInsights: this.marketScanResults?.raw_data || null
            }
        };
        
        const data = await graphQLClient.request(mutation, variables);
        
        if (data.generateWebsite) {
            // Poll for progress using subscription or polling
            await this.pollGraphQLProgress(data.generateWebsite.id);
        }
    } catch (error) {
        alert('Error generating website: ' + error.message);
        this.isGenerating = false;
    }
}

// Example: Poll Progress with GraphQL
async pollGraphQLProgress(websiteId) {
    const query = `
        query GetWebsiteStatus($id: ID!) {
            website(id: $id) {
                id
                status
                progress
                agentResults
                websiteFiles
                error
            }
        }
    `;
    
    const checkProgress = async () => {
        try {
            const data = await graphQLClient.request(query, { id: websiteId });
            const website = data.website;
            
            if (website.status === 'IN_PROGRESS') {
                this.progress = website.progress;
                this.currentAgent = `Processing... ${website.progress}%`;
                setTimeout(checkProgress, 2000);
            } else if (website.status === 'COMPLETED') {
                this.progress = 100;
                this.currentAgent = 'Complete!';
                
                // Add to results
                this.results.unshift({
                    id: website.id,
                    businessType: this.formData.businessType,
                    location: this.formData.location,
                    generatedAt: new Date().toLocaleString(),
                    websiteFiles: website.websiteFiles
                });
                
                this.isGenerating = false;
            } else if (website.status === 'FAILED') {
                throw new Error(website.error || 'Generation failed');
            }
        } catch (error) {
            console.error('Error checking progress:', error);
            this.isGenerating = false;
            alert('Error during generation: ' + error.message);
        }
    };
    
    checkProgress();
}
```

### 3. Backend GraphQL Integration

Create `/api/graphql` endpoint in your Flask app:

```python
from flask import Flask, request, jsonify
from graphql_server import GraphQLServer
from ranksavvy_graphql import schema, resolvers

app = Flask(__name__)

# Initialize GraphQL server
graphql_server = GraphQLServer(schema, resolvers)

@app.route('/api/graphql', methods=['POST'])
def graphql():
    """Handle GraphQL requests"""
    try:
        data = request.get_json()
        
        result = graphql_server.execute(
            data.get('query'),
            variables=data.get('variables'),
            context={
                'jina_client': jina_client,
                'claude_client': claude_client,
                'redis_client': redis_client
            }
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'errors': [{'message': str(e)}]}), 400
```

### 4. Add GraphQL Subscriptions for Real-time Updates

For real-time agent status updates:

```javascript
// WebSocket connection for subscriptions
const ws = new WebSocket('ws://localhost:5000/graphql-ws');

// Subscribe to agent updates
const subscription = `
    subscription OnAgentUpdate($websiteId: ID!) {
        agentUpdate(websiteId: $websiteId) {
            agentId
            agentName
            status
            progress
            message
            timestamp
        }
    }
`;

// Handle real-time updates
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'data') {
        const update = data.payload.data.agentUpdate;
        
        // Update UI with agent status
        this.currentAgent = update.agentName;
        this.progressMessage = update.message;
        
        // Update agent status in the agent list
        const agent = this.agents.find(a => a.id === update.agentId);
        if (agent) {
            agent.status = update.status === 'WORKING' ? 'active' : 'ready';
        }
    }
};
```

### 5. Benefits of GraphQL Integration

1. **Single Request for Multiple Data**: Fetch all needed data in one request
2. **Type Safety**: Strong typing ensures data consistency
3. **Real-time Updates**: Subscriptions for live agent status
4. **Efficient Queries**: Only request the data you need
5. **Better Error Handling**: Structured error responses

### 6. Example GraphQL Queries

```graphql
# Comprehensive market analysis
query MarketAnalysis($businessType: String!, $location: String!) {
    marketAnalysis(businessType: $businessType, location: $location) {
        competitors {
            name
            url
            strengths
            weaknesses
        }
        keywords {
            term
            volume
            difficulty
            opportunity
        }
        recommendations {
            strategy
            priority
            implementation
        }
    }
}

# Monitor multiple keywords
query KeywordRankings($domain: String!, $keywords: [String!]!) {
    keywordRankings(domain: $domain, keywords: $keywords) {
        keyword
        position
        change
        url
        searchVolume
        competitors {
            domain
            position
        }
    }
}

# Brand monitoring across platforms
query BrandMonitoring($brandName: String!) {
    brandMonitoring(brandName: $brandName) {
        platform
        mentions
        sentiment
        reach
        topPosts {
            url
            engagement
            sentiment
        }
    }
}
```

## Dark/Light Theme Implementation

The dark/light theme toggle has been implemented with:

1. **Theme Toggle Button**: Located in the header with sun/moon icons
2. **Persistent Storage**: Theme preference saved in localStorage
3. **Smooth Transitions**: All color changes animated with CSS transitions
4. **Complete Coverage**: All components support both themes

### Dark Mode Classes Added:
- `dark:bg-dark-bg` - Dark background
- `dark:bg-dark-card` - Dark card backgrounds
- `dark:text-dark-text` - Light text for dark mode
- `dark:border-dark-border` - Subtle borders in dark mode
- Custom gradients for dark mode headers

The theme automatically applies to:
- Main background and cards
- Text and icons
- Borders and shadows
- Agent status indicators
- Monitor popups
- Log entries with appropriate color contrast