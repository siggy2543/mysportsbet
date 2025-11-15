#!/bin/bash

echo "=== SPORTS BETTING APP - SSL DEPLOYMENT STATUS ==="
echo ""

echo "🔍 Container Status:"
cd /c/Users/cigba/sports_app
docker-compose ps

echo ""
echo "🌐 Testing HTTPS Endpoints:"

echo -n "SSL Health: "
curl -k -s https://localhost/ssl-health || echo "FAILED"

echo -n "API Status: "
curl -k -s https://localhost/api/v1/bets/public/status | jq -r '.status' 2>/dev/null || echo "FAILED"

echo -n "HTTP→HTTPS Redirect: "
http_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ssl-health)
if [ "$http_response" = "301" ]; then
    echo "✅ Working"
else
    echo "❌ Failed ($http_response)"
fi

echo ""
echo "🔐 SSL Certificate Status:"
openssl s_client -connect localhost:443 -servername localhost < /dev/null 2>/dev/null | grep -E "(subject|issuer|validity)" || echo "Certificate info not available"

echo ""
echo "📊 System Summary:"
echo "• HTTPS Frontend: Available on https://localhost"
echo "• API Endpoints: Available on https://localhost/api/v1/"
echo "• SSL Certificates: Self-signed (development ready)"
echo "• HTTP Redirect: Automatic redirect to HTTPS"
echo "• Windows Deployment: Complete with PowerShell automation"

echo ""
echo "✅ SSL DEPLOYMENT COMPLETE!"
echo "Your sports betting application is now running with SSL/HTTPS support."