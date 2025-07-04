# RankSavvy GraphQL Server

A powerful GraphQL API that combines Jina.ai search capabilities with Claude AI analysis for comprehensive SEO and market research.

## Features

- 🔍 **Multi-Platform Search**: Search across Google, Bing, YouTube, Reddit, and more
- 🎯 **Keyword Analysis**: Get keyword suggestions with search volume and difficulty
- 🏢 **Competitor Analysis**: Analyze competitor websites and strategies
- 📊 **Market Opportunity**: Assess market potential for businesses
- 📈 **Keyword Rankings**: Track keyword positions across domains
- 🔔 **Brand Monitoring**: Monitor brand mentions across platforms
- 🤖 **AI Analysis**: Leverage Claude for intelligent insights

## Setup

1. **Configure API Keys**
   Edit `.env` file and add your API keys:
   ```
   JINA_API_KEY=your_actual_jina_api_key
   ANTHROPIC_API_KEY=your_actual_claude_api_key
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start the Server**
   ```bash
   npm start
   ```

   The GraphQL playground will be available at: http://localhost:4000

## Example Queries

### Search Across Platforms
```graphql
query MultiPlatformSearch {
  seoSearch(
    query: "plumber Birmingham", 
    platforms: [GOOGLE, BING, YOUTUBE, REDDIT]
  ) {
    totalResults
    executionTime
    results {
      platform
      success
      data {
        title
        url
        position
      }
    }
  }
}
```

### Get Keyword Suggestions
```graphql
query KeywordIdeas {
  keywordSuggestions(seed: "hvac repair", location: "Birmingham AL") {
    totalSuggestions
    keywords {
      term
      searchVolume
      difficulty
      cpc
      trend
    }
  }
}
```

### Analyze Competitor
```graphql
query CompetitorInsights {
  competitorAnalysis(url: "example.com") {
    domain
    traffic {
      monthly
      growth
      sources {
        name
        percentage
      }
    }
    keywords {
      term
      searchVolume
    }
    backlinks
    technologies
  }
}
```

### Market Opportunity Assessment
```graphql
query MarketAnalysis {
  marketOpportunity(businessType: "HVAC Services", location: "Birmingham AL") {
    score
    competition
    potentialTraffic
    recommendations
  }
}
```

### Brand Monitoring
```graphql
query BrandTracking {
  brandMonitoring(brandName: "YourBrand") {
    totalMentions
    sentiment {
      positive
      neutral
      negative
    }
    platforms {
      platform
      mentions
      sentiment
      reach
      topPosts {
        url
        engagement
      }
    }
  }
}
```

## Integration with Frontend

The GraphQL server integrates seamlessly with the SEO Agent frontend. Update your frontend API calls to use GraphQL queries instead of REST endpoints for:

- More efficient data fetching
- Real-time updates via subscriptions
- Type-safe API contracts
- Better error handling

## Architecture

```
Frontend (Alpine.js) 
    ↓ GraphQL Queries
GraphQL Server (Apollo)
    ↓ API Calls
Jina.ai + Claude API
    ↓ Processed Data
Response to Frontend
```

## API Rate Limits

- Jina.ai: Check your plan limits
- Claude API: Based on your Anthropic tier
- Implement caching for frequently requested data

## Development

For development with auto-reload:
```bash
npm run dev
```

## Production Deployment

1. Set environment variables
2. Use PM2 or similar process manager
3. Configure reverse proxy (nginx/Apache)
4. Enable CORS for your frontend domain

## Error Handling

The server includes comprehensive error handling:
- API failures return graceful errors
- Network timeouts are handled
- Invalid queries return helpful messages

## Contributing

Feel free to submit issues and enhancement requests!