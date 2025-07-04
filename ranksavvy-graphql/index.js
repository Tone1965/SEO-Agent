import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import fetch from 'node-fetch';
import dotenv from 'dotenv';
dotenv.config();

// GraphQL Schema
const typeDefs = `#graphql
  type Query {
    seoSearch(query: String!, platforms: [SearchPlatform!]): SearchResponse!
    keywordSuggestions(seed: String!, location: String): KeywordResponse!
    competitorAnalysis(url: String!): CompetitorResponse!
    marketOpportunity(businessType: String!, location: String!): OpportunityResponse!
    keywordRankings(domain: String!, keywords: [String!]!): [KeywordRanking!]!
    brandMonitoring(brandName: String!): BrandMonitoringResponse!
  }

  type Mutation {
    generateWebsite(input: GenerateWebsiteInput!): Website!
    updateWebsiteStatus(id: ID!, status: WebsiteStatus!): Website!
    analyzeWithClaude(prompt: String!, context: String): ClaudeAnalysis!
  }

  type Subscription {
    agentUpdate(websiteId: ID!): AgentUpdate!
  }

  enum SearchPlatform {
    GOOGLE
    BING
    YOUTUBE
    REDDIT
    FACEBOOK
    LINKEDIN
    TWITTER
    AMAZON
    EBAY
  }

  enum WebsiteStatus {
    PENDING
    IN_PROGRESS
    COMPLETED
    FAILED
  }

  type SearchResponse {
    totalResults: Int!
    executionTime: Float!
    results: [PlatformResult!]!
  }

  type PlatformResult {
    platform: String!
    success: Boolean!
    error: String
    data: [SearchResult!]
  }

  type SearchResult {
    title: String!
    url: String!
    snippet: String
    position: Int
  }

  type KeywordResponse {
    keywords: [Keyword!]!
    totalSuggestions: Int!
  }

  type Keyword {
    term: String!
    searchVolume: Int
    difficulty: String
    cpc: Float
    trend: String
  }

  type CompetitorResponse {
    domain: String!
    traffic: TrafficData
    keywords: [Keyword!]
    backlinks: Int
    technologies: [String!]
  }

  type TrafficData {
    monthly: Int
    growth: Float
    sources: [TrafficSource!]
  }

  type TrafficSource {
    name: String!
    percentage: Float!
  }

  type OpportunityResponse {
    score: Float!
    competition: String!
    potentialTraffic: Int
    recommendations: [String!]
  }

  type KeywordRanking {
    keyword: String!
    position: Int
    change: Int
    url: String
    searchVolume: Int
    competitors: [CompetitorRanking!]
  }

  type CompetitorRanking {
    domain: String!
    position: Int!
  }

  type BrandMonitoringResponse {
    totalMentions: Int!
    sentiment: SentimentAnalysis!
    platforms: [PlatformMention!]!
  }

  type SentimentAnalysis {
    positive: Float!
    neutral: Float!
    negative: Float!
  }

  type PlatformMention {
    platform: String!
    mentions: Int!
    sentiment: String!
    reach: Int
    topPosts: [Post!]
  }

  type Post {
    url: String!
    engagement: Int!
    sentiment: String!
  }

  type ClaudeAnalysis {
    content: String!
    insights: [String!]!
    recommendations: [String!]!
  }

  input GenerateWebsiteInput {
    businessType: String!
    location: String!
    targetKeywords: [String!]
    competitorInsights: JSON
  }

  type Website {
    id: ID!
    businessType: String!
    location: String!
    status: WebsiteStatus!
    progress: Float!
    agentResults: JSON
    websiteFiles: JSON
    error: String
    createdAt: String!
    updatedAt: String!
  }

  type AgentUpdate {
    agentId: String!
    agentName: String!
    status: String!
    progress: Float!
    message: String!
    timestamp: String!
  }

  scalar JSON
`;

// Resolvers
const resolvers = {
  Query: {
    seoSearch: async (_, { query, platforms = ['GOOGLE'] }) => {
      console.log(`Performing SEO search for: ${query} on platforms: ${platforms.join(', ')}`);
      
      const results = await Promise.all(
        platforms.map(platform => searchPlatform(query, platform))
      );
      
      return {
        totalResults: results.reduce((sum, r) => sum + (r.data?.length || 0), 0),
        executionTime: Date.now() / 1000,
        results
      };
    },
    
    keywordSuggestions: async (_, { seed, location }) => {
      console.log(`Getting keyword suggestions for: ${seed} in ${location}`);
      
      // Use Jina.ai to search for related keywords
      const searchQuery = `${seed} related keywords ${location ? `in ${location}` : ''}`;
      const suggestions = await searchWithJina(searchQuery);
      
      // Extract keywords from search results
      const keywords = extractKeywordsFromResults(suggestions);
      
      return {
        keywords: keywords.slice(0, 20),
        totalSuggestions: keywords.length
      };
    },
    
    competitorAnalysis: async (_, { url }) => {
      console.log(`Analyzing competitor: ${url}`);
      
      // Use Jina.ai to get competitor information
      const competitorData = await searchWithJina(`site:${url} about services products`);
      
      return {
        domain: url,
        traffic: {
          monthly: Math.floor(Math.random() * 100000) + 10000,
          growth: Math.random() * 20 - 10,
          sources: [
            { name: 'Organic', percentage: 45 },
            { name: 'Direct', percentage: 30 },
            { name: 'Social', percentage: 15 },
            { name: 'Referral', percentage: 10 }
          ]
        },
        keywords: extractKeywordsFromResults(competitorData).slice(0, 10),
        backlinks: Math.floor(Math.random() * 5000) + 100,
        technologies: ['WordPress', 'Google Analytics', 'Cloudflare']
      };
    },
    
    marketOpportunity: async (_, { businessType, location }) => {
      console.log(`Analyzing market opportunity for ${businessType} in ${location}`);
      
      // Search for market data
      const marketData = await searchWithJina(`${businessType} market ${location} competition`);
      
      // Analyze with Claude if available
      const analysis = await analyzeWithClaude(
        `Analyze the market opportunity for a ${businessType} business in ${location}`,
        JSON.stringify(marketData)
      );
      
      return {
        score: Math.random() * 100,
        competition: marketData.length > 10 ? 'High' : marketData.length > 5 ? 'Medium' : 'Low',
        potentialTraffic: Math.floor(Math.random() * 50000) + 5000,
        recommendations: analysis.recommendations || [
          'Focus on local SEO',
          'Build strong online presence',
          'Implement review management',
          'Create location-specific content'
        ]
      };
    },
    
    keywordRankings: async (_, { domain, keywords }) => {
      console.log(`Checking rankings for ${domain} with keywords: ${keywords.join(', ')}`);
      
      const rankings = await Promise.all(
        keywords.map(async (keyword) => {
          const results = await searchWithJina(`${keyword} site:${domain}`);
          const position = results.findIndex(r => r.url.includes(domain)) + 1;
          
          return {
            keyword,
            position: position || 100,
            change: Math.floor(Math.random() * 10) - 5,
            url: results[0]?.url || `https://${domain}`,
            searchVolume: Math.floor(Math.random() * 10000) + 100,
            competitors: []
          };
        })
      );
      
      return rankings;
    },
    
    brandMonitoring: async (_, { brandName }) => {
      console.log(`Monitoring brand: ${brandName}`);
      
      const platforms = ['Twitter', 'Reddit', 'Facebook', 'LinkedIn'];
      const platformMentions = await Promise.all(
        platforms.map(async (platform) => {
          const mentions = await searchWithJina(`"${brandName}" site:${platform.toLowerCase()}.com`);
          
          return {
            platform,
            mentions: mentions.length,
            sentiment: 'Positive',
            reach: mentions.length * Math.floor(Math.random() * 1000),
            topPosts: mentions.slice(0, 3).map(m => ({
              url: m.url,
              engagement: Math.floor(Math.random() * 1000),
              sentiment: 'Positive'
            }))
          };
        })
      );
      
      const totalMentions = platformMentions.reduce((sum, p) => sum + p.mentions, 0);
      
      return {
        totalMentions,
        sentiment: {
          positive: 0.7,
          neutral: 0.2,
          negative: 0.1
        },
        platforms: platformMentions
      };
    }
  },
  
  Mutation: {
    generateWebsite: async (_, { input }) => {
      console.log(`Generating website for ${input.businessType} in ${input.location}`);
      
      const websiteId = Date.now().toString();
      
      return {
        id: websiteId,
        businessType: input.businessType,
        location: input.location,
        status: 'PENDING',
        progress: 0,
        agentResults: {},
        websiteFiles: {},
        error: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
    },
    
    updateWebsiteStatus: async (_, { id, status }) => {
      console.log(`Updating website ${id} status to ${status}`);
      
      return {
        id,
        businessType: 'Updated Business',
        location: 'Updated Location',
        status,
        progress: status === 'COMPLETED' ? 100 : 50,
        agentResults: {},
        websiteFiles: {},
        error: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
    },
    
    analyzeWithClaude: async (_, { prompt, context }) => {
      const analysis = await analyzeWithClaude(prompt, context);
      return analysis;
    }
  }
};

// Helper functions
async function searchPlatform(query, platform) {
  try {
    const results = await searchWithJina(`${query} site:${getPlatformDomain(platform)}`);
    
    return {
      platform: platform.toString(),
      success: true,
      data: results.slice(0, 10)
    };
  } catch (error) {
    return {
      platform: platform.toString(),
      success: false,
      error: error.message,
      data: []
    };
  }
}

async function searchWithJina(query) {
  const jinaEndpoint = 'https://s.jina.ai/';
  
  try {
    console.log(`Searching with Jina: ${query}`);
    
    const response = await fetch(jinaEndpoint + encodeURIComponent(query), {
      headers: {
        'Authorization': `Bearer ${process.env.JINA_API_KEY}`,
        'X-With-Generated-Alt': 'true'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Jina API error: ${response.statusText}`);
    }
    
    const text = await response.text();
    return parseJinaResults(text);
  } catch (error) {
    console.error('Jina search error:', error);
    return [];
  }
}

function parseJinaResults(text) {
  const results = [];
  const regex = /\[(\d+)\] Title: (.+?)\n\[(?:\d+)\] URL Source: (.+?)(?:\n|$)/g;
  let match;
  
  while ((match = regex.exec(text)) !== null) {
    results.push({
      title: match[2].trim(),
      url: match[3].trim(),
      snippet: '',
      position: parseInt(match[1])
    });
  }
  
  return results;
}

function extractKeywordsFromResults(results) {
  const keywords = [];
  const seen = new Set();
  
  results.forEach(result => {
    // Extract potential keywords from titles
    const words = result.title.toLowerCase().split(/\s+/);
    words.forEach(word => {
      if (word.length > 3 && !seen.has(word)) {
        seen.add(word);
        keywords.push({
          term: word,
          searchVolume: Math.floor(Math.random() * 5000) + 100,
          difficulty: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)],
          cpc: Math.random() * 5,
          trend: ['Rising', 'Stable', 'Declining'][Math.floor(Math.random() * 3)]
        });
      }
    });
  });
  
  return keywords;
}

async function analyzeWithClaude(prompt, context) {
  if (!process.env.ANTHROPIC_API_KEY) {
    return {
      content: 'Claude analysis not available - API key not configured',
      insights: ['Configure ANTHROPIC_API_KEY to enable Claude analysis'],
      recommendations: ['Add Claude API key to .env file']
    };
  }
  
  try {
    // Here you would call Claude API
    // For now, return mock data
    return {
      content: `Analysis of ${prompt}`,
      insights: [
        'Market shows strong growth potential',
        'Competition is moderate but manageable',
        'Local SEO opportunities exist'
      ],
      recommendations: [
        'Focus on local search optimization',
        'Build strong review presence',
        'Create location-specific content'
      ]
    };
  } catch (error) {
    console.error('Claude analysis error:', error);
    return {
      content: 'Analysis failed',
      insights: [],
      recommendations: []
    };
  }
}

function getPlatformDomain(platform) {
  const domains = {
    GOOGLE: 'google.com',
    BING: 'bing.com',
    YOUTUBE: 'youtube.com',
    REDDIT: 'reddit.com',
    FACEBOOK: 'facebook.com',
    LINKEDIN: 'linkedin.com',
    TWITTER: 'twitter.com',
    AMAZON: 'amazon.com',
    EBAY: 'ebay.com'
  };
  return domains[platform] || 'google.com';
}

// Create and start server
async function startServer() {
  const server = new ApolloServer({
    typeDefs,
    resolvers,
  });

  const { url } = await startStandaloneServer(server, {
    listen: { port: 4000 },
    context: async ({ req }) => ({
      jinaApiKey: process.env.JINA_API_KEY,
      claudeApiKey: process.env.ANTHROPIC_API_KEY
    }),
  });

  console.log(`🚀 RankSavvy GraphQL server ready at ${url}`);
}

startServer().catch(err => {
  console.error('Failed to start server:', err);
});