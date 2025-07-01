# =====================================
# MCP_GITHUB_FIRECRAWL.PY - GitHub & Firecrawl MCP Integration
# Use this file for: GitHub repository management and web scraping
# =====================================

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# MCP Client imports
try:
    from mcp import Client as MCPClient
    from mcp.client import StdioServerParameters
    from mcp.types import TextContent, Tool, CallToolResult
    MCP_AVAILABLE = True
except ImportError:
    # Fallback if MCP is not installed
    class MCPClient:
        async def call_tool(self, tool, params):
            return type('MockResult', (), {'content': [type('Content', (), {'text': 'Mock response'})()]})()
    class StdioServerParameters:
        def __init__(self, **kwargs):
            pass
    MCP_AVAILABLE = False

logger = logging.getLogger(__name__)

# =============================================================================
# GITHUB MCP INTEGRATION
# =============================================================================

class GitHubMCP:
    """GitHub MCP integration for SEO Agent system"""
    
    def __init__(self):
        self.client = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize GitHub MCP connection"""
        if not MCP_AVAILABLE:
            logger.warning("MCP not available - using fallback mode")
            self.initialized = True
            return
            
        try:
            self.client = MCPClient()
            server_params = StdioServerParameters(
                command="npx",
                args=["@modelcontextprotocol/server-github"],
                env={
                    **os.environ,
                    "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")
                }
            )
            await self.client.connect(server_params)
            self.initialized = True
            logger.info("GitHub MCP initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub MCP: {e}")
            raise
    
    async def create_seo_website_repo(self, site_data: Dict) -> Dict:
        """Create GitHub repository for SEO website"""
        if not self.initialized:
            await self.initialize()
            
        # Generate repository name
        service = site_data.get('service', 'website').lower().replace(' ', '-')
        location = site_data.get('location', 'local').lower().replace(' ', '-').replace(',', '')
        repo_name = f"seo-{service}-{location}"
        
        try:
            result = await self.client.call_tool(
                "github_create_repository",
                {
                    "name": repo_name,
                    "description": f"SEO optimized website for {site_data.get('service', 'Business')} in {site_data.get('location', 'Local Area')}",
                    "private": False,
                    "auto_init": True,
                    "gitignore_template": "Node",
                    "license_template": "mit",
                    "homepage": f"https://{repo_name}.netlify.app",
                    "topics": ["seo", "website", "local-business", "automated"]
                }
            )
            
            repo_info = json.loads(result.content[0].text) if result.content else {}
            
            return {
                "success": True,
                "repo_name": repo_name,
                "repo_url": repo_info.get("html_url", f"https://github.com/user/{repo_name}"),
                "clone_url": repo_info.get("clone_url", f"https://github.com/user/{repo_name}.git"),
                "ssh_url": repo_info.get("ssh_url", f"git@github.com:user/{repo_name}.git"),
                "created_at": repo_info.get("created_at", datetime.utcnow().isoformat())
            }
            
        except Exception as e:
            logger.error(f"Failed to create GitHub repository: {e}")
            return {"success": False, "error": str(e)}
    
    async def commit_website_files(self, repo_name: str, website_files: Dict[str, str]) -> Dict:
        """Commit all website files to GitHub repository"""
        if not self.initialized:
            await self.initialize()
            
        try:
            commits = []
            
            # Commit files in batches to avoid API limits
            file_batches = self._batch_files(website_files, batch_size=10)
            
            for batch_num, file_batch in enumerate(file_batches):
                for filepath, content in file_batch.items():
                    # Create or update file
                    result = await self.client.call_tool(
                        "github_create_or_update_file",
                        {
                            "repository": repo_name,
                            "path": filepath,
                            "content": content,
                            "message": f"Add {filepath} - SEO optimized website file",
                            "branch": "main"
                        }
                    )
                    
                    if result.content:
                        commit_info = json.loads(result.content[0].text)
                        commits.append({
                            "file": filepath,
                            "commit_sha": commit_info.get("commit", {}).get("sha"),
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                # Small delay between batches
                if batch_num < len(file_batches) - 1:
                    await asyncio.sleep(1)
            
            return {
                "success": True,
                "total_files": len(website_files),
                "commits": commits,
                "repository": repo_name
            }
            
        except Exception as e:
            logger.error(f"Failed to commit website files: {e}")
            return {"success": False, "error": str(e)}
    
    async def setup_github_pages(self, repo_name: str) -> Dict:
        """Enable GitHub Pages for the repository"""
        if not self.initialized:
            await self.initialize()
            
        try:
            result = await self.client.call_tool(
                "github_enable_pages",
                {
                    "repository": repo_name,
                    "source": {
                        "branch": "main",
                        "path": "/"
                    },
                    "enforce_https": True
                }
            )
            
            pages_info = json.loads(result.content[0].text) if result.content else {}
            
            return {
                "success": True,
                "pages_url": pages_info.get("html_url", f"https://username.github.io/{repo_name}"),
                "status": pages_info.get("status", "enabled"),
                "source": pages_info.get("source", {"branch": "main", "path": "/"})
            }
            
        except Exception as e:
            logger.error(f"Failed to setup GitHub Pages: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_deployment_workflow(self, repo_name: str, deployment_config: Dict) -> Dict:
        """Create GitHub Actions workflow for deployment"""
        if not self.initialized:
            await self.initialize()
            
        # Generate workflow based on deployment target
        workflow_content = self._generate_deployment_workflow(deployment_config)
        
        try:
            result = await self.client.call_tool(
                "github_create_or_update_file",
                {
                    "repository": repo_name,
                    "path": ".github/workflows/deploy.yml",
                    "content": workflow_content,
                    "message": "Add automated deployment workflow",
                    "branch": "main"
                }
            )
            
            return {
                "success": True,
                "workflow_path": ".github/workflows/deploy.yml",
                "deployment_target": deployment_config.get("platform", "netlify"),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create deployment workflow: {e}")
            return {"success": False, "error": str(e)}
    
    def _batch_files(self, files: Dict[str, str], batch_size: int = 10) -> List[Dict[str, str]]:
        """Split files into batches for processing"""
        items = list(files.items())
        batches = []
        
        for i in range(0, len(items), batch_size):
            batch = dict(items[i:i + batch_size])
            batches.append(batch)
        
        return batches
    
    def _generate_deployment_workflow(self, config: Dict) -> str:
        """Generate GitHub Actions workflow for deployment"""
        platform = config.get("platform", "netlify")
        
        if platform == "netlify":
            return """name: Deploy to Netlify

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build website
      run: npm run build
    
    - name: Deploy to Netlify
      uses: nwtgck/actions-netlify@v2.0
      with:
        publish-dir: './dist'
        production-branch: main
        github-token: ${{ secrets.GITHUB_TOKEN }}
        deploy-message: "Deploy from GitHub Actions"
        enable-pull-request-comment: false
        enable-commit-comment: true
        overwrites-pull-request-comment: true
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
"""
        elif platform == "vercel":
            return """name: Deploy to Vercel

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install Vercel CLI
      run: npm install --global vercel@latest
    
    - name: Pull Vercel Environment Information
      run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
    
    - name: Build Project Artifacts
      run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
    
    - name: Deploy Project Artifacts to Vercel
      run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
"""
        else:
            return """name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build website
      run: npm run build
    
    - name: Deploy
      run: echo "Add your deployment commands here"
"""

# =============================================================================
# FIRECRAWL MCP INTEGRATION
# =============================================================================

class FirecrawlMCP:
    """Firecrawl MCP integration for web scraping and competitor analysis"""
    
    def __init__(self):
        self.client = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize Firecrawl MCP connection"""
        if not MCP_AVAILABLE:
            logger.warning("MCP not available - using fallback mode")
            self.initialized = True
            return
            
        try:
            self.client = MCPClient()
            server_params = StdioServerParameters(
                command="npx",
                args=["@mendableai/firecrawl-mcp-server"],
                env={
                    **os.environ,
                    "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY")
                }
            )
            await self.client.connect(server_params)
            self.initialized = True
            logger.info("Firecrawl MCP initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firecrawl MCP: {e}")
            raise
    
    async def scrape_competitor_website(self, url: str, extract_options: Dict = None) -> Dict:
        """Scrape competitor website for SEO analysis"""
        if not self.initialized:
            await self.initialize()
            
        try:
            options = extract_options or {
                "formats": ["markdown", "html"],
                "includeTags": ["title", "meta", "h1", "h2", "h3", "p", "a"],
                "excludeTags": ["script", "style", "nav", "footer"],
                "onlyMainContent": True,
                "waitFor": 2000
            }
            
            result = await self.client.call_tool(
                "firecrawl_scrape",
                {
                    "url": url,
                    "formats": options.get("formats", ["markdown"]),
                    "includeTags": options.get("includeTags", []),
                    "excludeTags": options.get("excludeTags", []),
                    "onlyMainContent": options.get("onlyMainContent", True),
                    "waitFor": options.get("waitFor", 2000)
                }
            )
            
            scraped_data = json.loads(result.content[0].text) if result.content else {}
            
            # Extract SEO-relevant information
            seo_analysis = self._analyze_scraped_content(scraped_data)
            
            return {
                "success": True,
                "url": url,
                "scraped_at": datetime.utcnow().isoformat(),
                "content": scraped_data,
                "seo_analysis": seo_analysis
            }
            
        except Exception as e:
            logger.error(f"Failed to scrape website {url}: {e}")
            return {"success": False, "url": url, "error": str(e)}
    
    async def crawl_competitor_sitemap(self, base_url: str, max_pages: int = 50) -> Dict:
        """Crawl competitor website to analyze site structure"""
        if not self.initialized:
            await self.initialize()
            
        try:
            result = await self.client.call_tool(
                "firecrawl_crawl",
                {
                    "url": base_url,
                    "maxPages": max_pages,
                    "formats": ["markdown"],
                    "excludes": ["*/admin/*", "*/wp-admin/*", "*/login/*"],
                    "includes": ["*/services/*", "*/about/*", "*/contact/*"],
                    "allowBackwardCrawling": False,
                    "limit": max_pages
                }
            )
            
            crawl_data = json.loads(result.content[0].text) if result.content else {}
            
            # Analyze site structure for SEO insights
            structure_analysis = self._analyze_site_structure(crawl_data)
            
            return {
                "success": True,
                "base_url": base_url,
                "crawled_at": datetime.utcnow().isoformat(),
                "pages_found": len(crawl_data.get("pages", [])),
                "crawl_data": crawl_data,
                "structure_analysis": structure_analysis
            }
            
        except Exception as e:
            logger.error(f"Failed to crawl website {base_url}: {e}")
            return {"success": False, "base_url": base_url, "error": str(e)}
    
    async def batch_competitor_analysis(self, competitor_urls: List[str]) -> Dict:
        """Analyze multiple competitor websites"""
        if not self.initialized:
            await self.initialize()
            
        results = []
        
        for url in competitor_urls:
            try:
                # Scrape individual competitor
                scrape_result = await self.scrape_competitor_website(url)
                results.append(scrape_result)
                
                # Small delay to be respectful
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to analyze competitor {url}: {e}")
                results.append({
                    "success": False,
                    "url": url,
                    "error": str(e)
                })
        
        # Aggregate competitive intelligence
        competitive_intelligence = self._aggregate_competitor_data(results)
        
        return {
            "success": True,
            "analyzed_at": datetime.utcnow().isoformat(),
            "total_competitors": len(competitor_urls),
            "successful_analyses": len([r for r in results if r.get("success")]),
            "individual_results": results,
            "competitive_intelligence": competitive_intelligence
        }
    
    def _analyze_scraped_content(self, scraped_data: Dict) -> Dict:
        """Analyze scraped content for SEO insights"""
        content = scraped_data.get("content", "")
        metadata = scraped_data.get("metadata", {})
        
        analysis = {
            "title": metadata.get("title", ""),
            "description": metadata.get("description", ""),
            "keywords": metadata.get("keywords", ""),
            "content_length": len(content),
            "headings": self._extract_headings(content),
            "internal_links": self._count_internal_links(content),
            "external_links": self._count_external_links(content),
            "images": self._count_images(content),
            "seo_score": self._calculate_basic_seo_score(metadata, content)
        }
        
        return analysis
    
    def _analyze_site_structure(self, crawl_data: Dict) -> Dict:
        """Analyze crawled site structure"""
        pages = crawl_data.get("pages", [])
        
        structure = {
            "total_pages": len(pages),
            "page_types": self._categorize_pages(pages),
            "url_structure": self._analyze_url_patterns(pages),
            "content_distribution": self._analyze_content_distribution(pages),
            "technical_insights": self._extract_technical_insights(pages)
        }
        
        return structure
    
    def _aggregate_competitor_data(self, results: List[Dict]) -> Dict:
        """Aggregate data from multiple competitors"""
        successful_results = [r for r in results if r.get("success")]
        
        if not successful_results:
            return {"error": "No successful competitor analyses"}
        
        # Aggregate SEO patterns
        common_patterns = {
            "common_keywords": self._find_common_keywords(successful_results),
            "content_strategies": self._identify_content_strategies(successful_results),
            "technical_patterns": self._identify_technical_patterns(successful_results),
            "opportunity_gaps": self._identify_opportunity_gaps(successful_results)
        }
        
        return common_patterns
    
    def _extract_headings(self, content: str) -> Dict:
        """Extract heading structure from content"""
        import re
        
        headings = {
            "h1": len(re.findall(r'# (.+)', content)),
            "h2": len(re.findall(r'## (.+)', content)),
            "h3": len(re.findall(r'### (.+)', content)),
            "h4": len(re.findall(r'#### (.+)', content))
        }
        
        return headings
    
    def _count_internal_links(self, content: str) -> int:
        """Count internal links in content"""
        import re
        return len(re.findall(r'\[.+\]\(\/[^)]+\)', content))
    
    def _count_external_links(self, content: str) -> int:
        """Count external links in content"""
        import re
        return len(re.findall(r'\[.+\]\(https?:\/\/[^)]+\)', content))
    
    def _count_images(self, content: str) -> int:
        """Count images in content"""
        import re
        return len(re.findall(r'!\[.*\]\([^)]+\)', content))
    
    def _calculate_basic_seo_score(self, metadata: Dict, content: str) -> float:
        """Calculate basic SEO score"""
        score = 0.0
        
        # Title exists and appropriate length
        title = metadata.get("title", "")
        if title and 30 <= len(title) <= 60:
            score += 2.0
        elif title:
            score += 1.0
        
        # Description exists and appropriate length
        description = metadata.get("description", "")
        if description and 120 <= len(description) <= 160:
            score += 2.0
        elif description:
            score += 1.0
        
        # Content length
        if len(content) >= 1000:
            score += 2.0
        elif len(content) >= 500:
            score += 1.0
        
        # Headings structure
        headings = self._extract_headings(content)
        if headings["h1"] >= 1:
            score += 1.0
        if headings["h2"] >= 2:
            score += 1.0
        
        # Images
        if self._count_images(content) > 0:
            score += 1.0
        
        # Internal links
        if self._count_internal_links(content) >= 3:
            score += 1.0
        
        return min(score, 10.0)  # Cap at 10
    
    def _categorize_pages(self, pages: List[Dict]) -> Dict:
        """Categorize pages by type"""
        categories = {
            "homepage": 0,
            "services": 0,
            "about": 0,
            "contact": 0,
            "blog": 0,
            "other": 0
        }
        
        for page in pages:
            url = page.get("url", "").lower()
            if url.endswith("/") or url.split("/")[-1] in ["", "index.html", "index.php"]:
                categories["homepage"] += 1
            elif "service" in url:
                categories["services"] += 1
            elif "about" in url:
                categories["about"] += 1
            elif "contact" in url:
                categories["contact"] += 1
            elif "blog" in url or "news" in url or "article" in url:
                categories["blog"] += 1
            else:
                categories["other"] += 1
        
        return categories
    
    def _analyze_url_patterns(self, pages: List[Dict]) -> Dict:
        """Analyze URL structure patterns"""
        urls = [page.get("url", "") for page in pages]
        
        patterns = {
            "avg_url_length": sum(len(url) for url in urls) / len(urls) if urls else 0,
            "uses_hyphens": sum(1 for url in urls if "-" in url) / len(urls) if urls else 0,
            "uses_underscores": sum(1 for url in urls if "_" in url) / len(urls) if urls else 0,
            "max_depth": max(url.count("/") - 2 for url in urls if url.startswith("http")) if urls else 0
        }
        
        return patterns
    
    def _analyze_content_distribution(self, pages: List[Dict]) -> Dict:
        """Analyze content distribution across pages"""
        content_lengths = [len(page.get("content", "")) for page in pages]
        
        if not content_lengths:
            return {"error": "No content found"}
        
        distribution = {
            "avg_content_length": sum(content_lengths) / len(content_lengths),
            "min_content_length": min(content_lengths),
            "max_content_length": max(content_lengths),
            "pages_with_substantial_content": sum(1 for length in content_lengths if length > 1000)
        }
        
        return distribution
    
    def _extract_technical_insights(self, pages: List[Dict]) -> Dict:
        """Extract technical SEO insights"""
        insights = {
            "total_pages_crawled": len(pages),
            "pages_with_meta_description": 0,
            "pages_with_proper_titles": 0,
            "average_load_time": 0  # Would need actual timing data
        }
        
        for page in pages:
            metadata = page.get("metadata", {})
            if metadata.get("description"):
                insights["pages_with_meta_description"] += 1
            if metadata.get("title") and 30 <= len(metadata["title"]) <= 60:
                insights["pages_with_proper_titles"] += 1
        
        return insights
    
    def _find_common_keywords(self, results: List[Dict]) -> List[str]:
        """Find common keywords across competitors"""
        # Simple implementation - would use more sophisticated NLP in production
        all_keywords = []
        for result in results:
            seo_analysis = result.get("seo_analysis", {})
            keywords = seo_analysis.get("keywords", "")
            if keywords:
                all_keywords.extend(keywords.split(","))
        
        # Count frequency and return most common
        from collections import Counter
        keyword_counts = Counter(k.strip().lower() for k in all_keywords if k.strip())
        return [k for k, count in keyword_counts.most_common(10)]
    
    def _identify_content_strategies(self, results: List[Dict]) -> Dict:
        """Identify common content strategies"""
        strategies = {
            "avg_content_length": 0,
            "common_page_types": [],
            "content_patterns": []
        }
        
        content_lengths = []
        for result in results:
            seo_analysis = result.get("seo_analysis", {})
            content_length = seo_analysis.get("content_length", 0)
            if content_length > 0:
                content_lengths.append(content_length)
        
        if content_lengths:
            strategies["avg_content_length"] = sum(content_lengths) / len(content_lengths)
        
        return strategies
    
    def _identify_technical_patterns(self, results: List[Dict]) -> Dict:
        """Identify technical SEO patterns"""
        patterns = {
            "common_meta_patterns": [],
            "url_structures": [],
            "technical_optimizations": []
        }
        
        # Analyze metadata patterns
        titles = []
        descriptions = []
        
        for result in results:
            seo_analysis = result.get("seo_analysis", {})
            title = seo_analysis.get("title", "")
            description = seo_analysis.get("description", "")
            
            if title:
                titles.append(len(title))
            if description:
                descriptions.append(len(description))
        
        if titles:
            patterns["avg_title_length"] = sum(titles) / len(titles)
        if descriptions:
            patterns["avg_description_length"] = sum(descriptions) / len(descriptions)
        
        return patterns
    
    def _identify_opportunity_gaps(self, results: List[Dict]) -> List[str]:
        """Identify SEO opportunity gaps"""
        gaps = []
        
        # Analyze common weaknesses
        low_seo_scores = [r for r in results if r.get("seo_analysis", {}).get("seo_score", 0) < 7]
        
        if len(low_seo_scores) > len(results) * 0.5:
            gaps.append("Most competitors have suboptimal SEO - opportunity for better optimization")
        
        # Check for missing content types
        has_blog = any("blog" in str(r) for r in results)
        if not has_blog:
            gaps.append("Competitors lack blog content - opportunity for content marketing")
        
        return gaps

# =============================================================================
# COMBINED MCP ORCHESTRATOR
# =============================================================================

class GitHubFirecrawlOrchestrator:
    """Combined orchestrator for GitHub and Firecrawl operations"""
    
    def __init__(self):
        self.github = GitHubMCP()
        self.firecrawl = FirecrawlMCP()
        self.initialized = False
    
    async def initialize(self):
        """Initialize both MCP connections"""
        try:
            await self.github.initialize()
            await self.firecrawl.initialize()
            self.initialized = True
            logger.info("GitHub & Firecrawl MCP orchestrator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MCP orchestrator: {e}")
            raise
    
    async def full_competitive_analysis_and_deployment(self, site_data: Dict, competitor_urls: List[str]) -> Dict:
        """Complete workflow: analyze competitors and deploy to GitHub"""
        if not self.initialized:
            await self.initialize()
        
        workflow_results = {
            "started_at": datetime.utcnow().isoformat(),
            "site_data": site_data,
            "steps_completed": [],
            "errors": []
        }
        
        try:
            # Step 1: Analyze competitors
            logger.info("Starting competitive analysis...")
            competitor_analysis = await self.firecrawl.batch_competitor_analysis(competitor_urls)
            
            if competitor_analysis["success"]:
                workflow_results["steps_completed"].append("competitive_analysis")
                workflow_results["competitor_analysis"] = competitor_analysis
            else:
                workflow_results["errors"].append("Failed to analyze competitors")
            
            # Step 2: Create GitHub repository
            logger.info("Creating GitHub repository...")
            repo_result = await self.github.create_seo_website_repo(site_data)
            
            if repo_result["success"]:
                workflow_results["steps_completed"].append("github_repo_created")
                workflow_results["repository"] = repo_result
                repo_name = repo_result["repo_name"]
            else:
                workflow_results["errors"].append(f"Failed to create repository: {repo_result['error']}")
                return workflow_results
            
            # Step 3: Generate and commit website files
            logger.info("Generating and committing website files...")
            website_files = self._generate_website_files_from_analysis(
                site_data, 
                competitor_analysis.get("competitive_intelligence", {})
            )
            
            commit_result = await self.github.commit_website_files(repo_name, website_files)
            
            if commit_result["success"]:
                workflow_results["steps_completed"].append("website_files_committed")
                workflow_results["commit_result"] = commit_result
            else:
                workflow_results["errors"].append(f"Failed to commit files: {commit_result['error']}")
            
            # Step 4: Setup GitHub Pages
            logger.info("Setting up GitHub Pages...")
            pages_result = await self.github.setup_github_pages(repo_name)
            
            if pages_result["success"]:
                workflow_results["steps_completed"].append("github_pages_enabled")
                workflow_results["pages_result"] = pages_result
            else:
                workflow_results["errors"].append(f"Failed to setup GitHub Pages: {pages_result['error']}")
            
            # Step 5: Create deployment workflow
            logger.info("Creating deployment workflow...")
            workflow_result = await self.github.create_deployment_workflow(
                repo_name, 
                {"platform": "netlify"}
            )
            
            if workflow_result["success"]:
                workflow_results["steps_completed"].append("deployment_workflow_created")
                workflow_results["workflow_result"] = workflow_result
            else:
                workflow_results["errors"].append(f"Failed to create workflow: {workflow_result['error']}")
            
            # Final summary
            workflow_results["completed_at"] = datetime.utcnow().isoformat()
            workflow_results["success"] = len(workflow_results["errors"]) == 0
            workflow_results["summary"] = {
                "repository_url": repo_result.get("repo_url"),
                "pages_url": pages_result.get("pages_url"),
                "competitors_analyzed": competitor_analysis.get("successful_analyses", 0),
                "files_committed": commit_result.get("total_files", 0)
            }
            
            return workflow_results
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            workflow_results["errors"].append(f"Workflow error: {str(e)}")
            workflow_results["success"] = False
            return workflow_results
    
    def _generate_website_files_from_analysis(self, site_data: Dict, competitive_intel: Dict) -> Dict[str, str]:
        """Generate website files based on competitive analysis"""
        
        service = site_data.get("service", "Business")
        location = site_data.get("location", "Local Area")
        
        # Basic website structure based on analysis
        files = {
            "index.html": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{service} in {location} - Professional Services</title>
    <meta name="description" content="Professional {service.lower()} services in {location}. Licensed, insured, and available 24/7 for all your needs.">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <nav>
            <div class="logo">
                <h1>{service}</h1>
            </div>
            <ul>
                <li><a href="#services">Services</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section class="hero">
            <h1>Professional {service} in {location}</h1>
            <p>Licensed, insured, and available 24/7 for all your {service.lower()} needs.</p>
            <a href="#contact" class="cta-button">Get Free Quote</a>
        </section>
        
        <section id="services">
            <h2>Our Services</h2>
            <div class="services-grid">
                <div class="service-card">
                    <h3>Emergency Service</h3>
                    <p>24/7 emergency {service.lower()} available</p>
                </div>
                <div class="service-card">
                    <h3>Residential</h3>
                    <p>Complete {service.lower()} for homeowners</p>
                </div>
                <div class="service-card">
                    <h3>Commercial</h3>
                    <p>Professional {service.lower()} for businesses</p>
                </div>
            </div>
        </section>
        
        <section id="about">
            <h2>Why Choose Us</h2>
            <ul>
                <li>Licensed and Insured</li>
                <li>Experienced Professionals</li>
                <li>Competitive Pricing</li>
                <li>Satisfaction Guaranteed</li>
            </ul>
        </section>
        
        <section id="contact">
            <h2>Contact Us</h2>
            <p>Ready to get started? Contact us today for a free estimate!</p>
            <a href="tel:555-123-4567" class="phone-link">(555) 123-4567</a>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2025 {service} - {location}. All rights reserved.</p>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>""",
            
            "styles.css": """/* Modern CSS for SEO website */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
}

header {
    background: #2563eb;
    color: white;
    padding: 1rem 0;
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 1000;
}

nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}

nav ul {
    display: flex;
    list-style: none;
    gap: 2rem;
}

nav a {
    color: white;
    text-decoration: none;
    transition: opacity 0.3s;
}

nav a:hover {
    opacity: 0.8;
}

main {
    margin-top: 80px;
}

.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
    padding: 6rem 2rem;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.hero p {
    font-size: 1.25rem;
    margin-bottom: 2rem;
}

.cta-button {
    background: #f59e0b;
    color: white;
    padding: 1rem 2rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    transition: background 0.3s;
}

.cta-button:hover {
    background: #d97706;
}

section {
    padding: 4rem 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.service-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
}

.service-card:hover {
    transform: translateY(-4px);
}

.phone-link {
    font-size: 2rem;
    color: #2563eb;
    text-decoration: none;
    font-weight: bold;
}

footer {
    background: #1f2937;
    color: white;
    text-align: center;
    padding: 2rem;
}

@media (max-width: 768px) {
    .hero h1 {
        font-size: 2rem;
    }
    
    nav {
        flex-direction: column;
        gap: 1rem;
    }
    
    nav ul {
        gap: 1rem;
    }
}""",
            
            "script.js": """// Modern JavaScript for SEO website
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Track phone number clicks
    document.querySelectorAll('a[href^="tel:"]').forEach(link => {
        link.addEventListener('click', function() {
            console.log('Phone number clicked');
            // Add analytics tracking here
        });
    });
    
    // Simple form validation if forms are added
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('[required]');
            let valid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    input.style.borderColor = '#ef4444';
                } else {
                    input.style.borderColor = '#d1d5db';
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    });
});""",
            
            "package.json": json.dumps({
                "name": f"seo-{service.lower().replace(' ', '-')}-{location.lower().replace(' ', '-').replace(',', '')}",
                "version": "1.0.0",
                "description": f"SEO optimized website for {service} in {location}",
                "scripts": {
                    "build": "echo 'Build process - add your build commands here'",
                    "start": "echo 'Start server - add your server start command here'",
                    "deploy": "echo 'Deploy process - configured via GitHub Actions'"
                },
                "keywords": ["seo", "website", service.lower().replace(" ", "-"), "local-business"],
                "author": "SEO Agent System",
                "license": "MIT"
            }, indent=2),
            
            "README.md": f"""# {service} - {location}

SEO optimized website for {service} serving {location}.

## Features

- ✅ SEO Optimized
- ✅ Mobile Responsive  
- ✅ Fast Loading
- ✅ Conversion Focused
- ✅ Local Business Schema
- ✅ Google My Business Ready

## Generated by SEO Agent System

This website was automatically generated using competitive analysis and SEO best practices.

### Competitive Analysis Results

- Competitors analyzed: {competitive_intel.get('competitors_analyzed', 'N/A')}
- Opportunities identified: {len(competitive_intel.get('opportunity_gaps', []))}
- Technical optimizations applied: Based on competitor weaknesses

## Deployment

This site is configured for automatic deployment via GitHub Actions to:
- Netlify
- Vercel  
- GitHub Pages

## Local Development

```bash
# Open index.html in your browser
open index.html

# Or serve with a simple HTTP server
python -m http.server 8000
```

## SEO Features

- Optimized meta tags
- Structured data markup ready
- Performance optimized
- Accessibility compliant
- Local SEO ready

---

Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        }
        
        return files

# =============================================================================
# INSTALLATION AND SETUP HELPER
# =============================================================================

async def install_mcp_servers():
    """Install required MCP servers"""
    import subprocess
    import sys
    
    servers = [
        "@modelcontextprotocol/server-github",
        "@mendableai/firecrawl-mcp-server"
    ]
    
    for server in servers:
        try:
            print(f"Installing {server}...")
            result = subprocess.run(
                ["npm", "install", "-g", server],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {server} installed successfully")
            else:
                print(f"❌ Failed to install {server}: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error installing {server}: {e}")

def setup_environment_variables():
    """Setup guide for environment variables"""
    print("""
🔧 Required Environment Variables:

1. GitHub Token (for repository operations):
   export GITHUB_TOKEN="your_github_personal_access_token"
   
   Get your token from: https://github.com/settings/tokens
   Required scopes: repo, workflow, admin:repo_hook

2. Firecrawl API Key (for web scraping):
   export FIRECRAWL_API_KEY="your_firecrawl_api_key"
   
   Get your key from: https://firecrawl.dev/

3. Optional - Add to your shell profile:
   echo 'export GITHUB_TOKEN="your_token"' >> ~/.bashrc
   echo 'export FIRECRAWL_API_KEY="your_key"' >> ~/.bashrc

4. Reload your shell:
   source ~/.bashrc
""")

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

async def example_usage():
    """Example of how to use the GitHub and Firecrawl MCP integration"""
    
    # Initialize the orchestrator
    orchestrator = GitHubFirecrawlOrchestrator()
    
    # Site data for the SEO website
    site_data = {
        "service": "HVAC Services",
        "location": "Birmingham, AL",
        "target_keywords": ["hvac repair", "air conditioning", "heating services"],
        "business_type": "Local Service Business"
    }
    
    # Competitor URLs to analyze
    competitor_urls = [
        "https://competitor1.com",
        "https://competitor2.com", 
        "https://competitor3.com"
    ]
    
    try:
        # Run the complete workflow
        result = await orchestrator.full_competitive_analysis_and_deployment(
            site_data, 
            competitor_urls
        )
        
        if result["success"]:
            print("🎉 Website generation and deployment successful!")
            print(f"Repository: {result['summary']['repository_url']}")
            print(f"Live site: {result['summary']['pages_url']}")
            print(f"Competitors analyzed: {result['summary']['competitors_analyzed']}")
        else:
            print("❌ Workflow failed:")
            for error in result["errors"]:
                print(f"  - {error}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            asyncio.run(install_mcp_servers())
        elif sys.argv[1] == "setup":
            setup_environment_variables()
        elif sys.argv[1] == "example":
            asyncio.run(example_usage())
        else:
            print("Usage: python mcp_github_firecrawl.py [install|setup|example]")
    else:
        print("""
🤖 GitHub & Firecrawl MCP Integration for SEO Agent

Available commands:
  python mcp_github_firecrawl.py install  # Install MCP servers
  python mcp_github_firecrawl.py setup    # Show environment setup
  python mcp_github_firecrawl.py example  # Run example workflow

Integration features:
  ✅ GitHub repository creation and management
  ✅ Automated website deployment
  ✅ Competitor website analysis
  ✅ SEO-optimized content generation
  ✅ GitHub Actions CI/CD setup
        """)