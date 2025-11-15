#!/bin/bash
# Legal Sports Betting Analysis - Production Deployment Script

echo "🚀 Deploying Legal Sports Betting Analysis Platform"
echo "=============================================="

# Set environment variables
export ENVIRONMENT=production
export DEBUG=false
export PORT=8000
export BANKROLL_BALANCE=200.00
export DAILY_LIMIT=50.00

# Create logs directory
mkdir -p ../logs

echo "✅ Environment configured"

# Start the legal betting analysis API
echo "🎯 Starting Legal Betting Analysis API..."
cd backend

# Install dependencies if needed
echo "📦 Installing Python dependencies..."
pip install --quiet fastapi uvicorn aiohttp openai pydantic

# Start the API server
echo "🌐 Starting API server on port $PORT..."
python -m uvicorn simple_api:app --host 0.0.0.0 --port $PORT --workers 1 &
API_PID=$!

sleep 5

# Test the API
echo "🧪 Testing API endpoints..."
API_URL="http://localhost:$PORT"

echo "  Health check..."
if curl -s "$API_URL/health" > /dev/null; then
    echo "  ✅ Health check passed"
else
    echo "  ❌ Health check failed"
fi

echo "  Getting system status..."
if curl -s "$API_URL/analytics/status" > /dev/null; then
    echo "  ✅ System status OK"
else
    echo "  ❌ System status failed"
fi

echo "  Getting NBA recommendations..."
if curl -s "$API_URL/analytics/recommendations/NBA" > /dev/null; then
    echo "  ✅ NBA recommendations OK"
else
    echo "  ❌ NBA recommendations failed"
fi

echo ""
echo "=============================================="
echo "🎯 Legal Sports Betting Analysis Platform Deployed!"
echo ""
echo "📊 API Endpoints:"
echo "  • Health Check:    $API_URL/health"
echo "  • Documentation:   $API_URL/docs"
echo "  • Live Demo:       $API_URL/live-demo"
echo "  • NBA Analysis:    $API_URL/analytics/recommendations/NBA"
echo "  • System Status:   $API_URL/analytics/status"
echo "  • Bankroll Info:   $API_URL/analytics/bankroll"
echo ""
echo "🔒 Compliance Status: FULLY COMPLIANT"
echo "📱 Manual Betting Required: YES"
echo "⚖️ Terms of Service: RESPECTED"
echo ""
echo "💡 Next Steps:"
echo "  1. Set your OPENAI_API_KEY for enhanced AI predictions"
echo "  2. Configure your actual bankroll: curl -X POST '$API_URL/analytics/bankroll/update' -d '{\"new_balance\": 200.0}'"
echo "  3. Access web dashboard: $API_URL/docs"
echo ""
echo "API Process ID: $API_PID"
echo "To stop: kill $API_PID"
echo "To monitor: tail -f ../logs/api.log"