#!/bin/bash
echo "🔍 Checking SEO Agent Deployment..."
echo ""
echo "1. Check if workshop.html exists locally:"
ls -la frontend/workshop.html
echo ""
echo "2. Check main site:"
curl -s -o /dev/null -w "Main site (/) status: %{http_code}\n" http://142.93.194.81/
echo ""
echo "3. Check workshop direct HTML:"
curl -s -o /dev/null -w "Workshop HTML (/frontend/workshop.html) status: %{http_code}\n" http://142.93.194.81/frontend/workshop.html
echo ""
echo "4. Check if API is responding:"
curl -s -o /dev/null -w "API health check status: %{http_code}\n" http://142.93.194.81/api/health
echo ""
echo "5. Try accessing workshop.html directly:"
curl -s -o /dev/null -w "Workshop page (/workshop.html) status: %{http_code}\n" http://142.93.194.81/workshop.html
echo ""
echo "If you see 404 for workshop.html, the file hasn't been deployed yet."
echo "If you see 502 for API endpoints, the Flask app isn't running properly."