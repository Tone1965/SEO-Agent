# =====================================
# DOCKERFILE - PRODUCTION SEO AGENT SYSTEM
# =====================================
# Multi-stage build for optimized production deployment

# Stage 1: Python dependencies and app setup
FROM python:3.11-slim as python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers for web scraping
RUN playwright install --with-deps chromium

# Stage 2: Node.js for MCP servers and frontend tools
FROM python-base as final

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install global npm packages for MCP servers
RUN npm install -g @modelcontextprotocol/server-github firecrawl-mcp

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/generated_websites /app/uploads

# Set proper permissions
RUN chmod +x /app/mcp_servers/gitwait_server.py

# Create non-root user for security
RUN groupadd -r seoagent && useradd -r -g seoagent seoagent
RUN chown -R seoagent:seoagent /app
USER seoagent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "300", "--worker-class", "gevent", "main:app"]