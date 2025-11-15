# Legal Sports Betting Analysis Platform - Deployment Guide

## 🎯 Overview

This is a **LEGAL, COMPLIANT** sports betting analysis platform that provides AI-powered betting recommendations while requiring manual bet placement through official channels. This system:

- ✅ **Complies with all platform Terms of Service**
- ✅ **Requires manual bet placement**
- ✅ **Uses legitimate free sports data APIs**
- ✅ **Provides analysis only - no automated betting**
- ✅ **Implements proper risk management**

## 🚀 Quick Start (Legal Production)

### 1. Start the Legal Production System

```bash
# Start the legal betting analysis platform
docker-compose -f docker-compose.legal.yml up -d

# Check system status
curl http://localhost:8000/health
```

### 2. Access Your Analysis Dashboard

- **API Documentation**: http://localhost:8000/docs
- **Live Demo**: http://localhost:8000/live-demo
- **Web Dashboard**: http://localhost:3000 (when frontend is built)

### 3. Get AI Betting Recommendations

```bash
# Get NBA betting recommendations
curl "http://localhost:8000/analytics/recommendations/NBA"

# Get live games
curl "http://localhost:8000/analytics/live-games/NBA"

# Check your bankroll status
curl "http://localhost:8000/analytics/bankroll"
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://sports_user:sports_pass@localhost:5432/sports_betting

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI (for AI predictions)
OPENAI_API_KEY=your_openai_api_key_here

# Application
ENVIRONMENT=production
DEBUG=false
PORT=8000

# Betting Configuration
BANKROLL_BALANCE=200.00
DAILY_LIMIT=50.00
KELLY_MULTIPLIER=0.25
MAX_BET_PERCENTAGE=0.05
```

### Bankroll Management

```bash
# Update your bankroll balance
curl -X POST "http://localhost:8000/analytics/bankroll/update" \
  -H "Content-Type: application/json" \
  -d '{"new_balance": 200.0}'

# Log a bet result (after manual placement)
curl -X POST "http://localhost:8000/analytics/bet-result" \
  -H "Content-Type: application/json" \
  -d '{
    "recommendation_id": "nba_game_1",
    "amount": 10.0,
    "won": true,
    "payout": 18.5
  }'
```

## 📊 How It Works

### 1. AI Analysis Process

1. **Data Collection**: System fetches live sports data from legitimate APIs (ESPN, etc.)
2. **AI Analysis**: OpenAI models analyze games and generate predictions
3. **Risk Assessment**: Kelly Criterion calculates optimal bet sizes
4. **Recommendations**: System provides detailed betting recommendations

### 2. Manual Betting Workflow

1. **Get Recommendations**: API provides AI-powered betting opportunities
2. **Review Analysis**: Check confidence levels, expected value, and reasoning
3. **Calculate Bet Size**: Use Kelly Criterion suggestions
4. **Manual Placement**: Log into DraftKings website/app and place bets manually
5. **Log Results**: Update system with bet outcomes for tracking

### 3. Example API Response

```json
{
  "game_id": "nba_game_1",
  "matchup": "Lakers @ Warriors",
  "sport": "NBA",
  "recommended_bet": "Lakers Moneyline",
  "confidence": "78.5%",
  "expected_value": 0.125,
  "suggested_bet_size": "$12.50",
  "kelly_percentage": "6.2%",
  "odds": {
    "home_ml": -110,
    "away_ml": -110,
    "recommended_odds": -110
  },
  "reasoning": "AI model predicts Lakers victory with 78.5% confidence based on recent form, matchup analysis, and statistical indicators.",
  "risk_level": "low",
  "manual_betting_required": true,
  "instructions": "Place this bet manually through official DraftKings website/app"
}
```

## 🛡️ Legal Compliance

### Why This Approach is Legal

1. **Analysis Only**: System provides recommendations, not automated betting
2. **Manual Execution**: All bets must be placed manually by the user
3. **No ToS Violations**: Does not automate or bot any betting platforms
4. **Legitimate APIs**: Uses only free, public sports data APIs
5. **User Control**: User maintains full control over all betting decisions

### Safety Features

- **Risk Management**: Kelly Criterion bet sizing with conservative multipliers
- **Daily Limits**: Configurable daily betting limits
- **Performance Tracking**: Monitor success rates and P&L
- **Compliance Monitoring**: Ensures all operations remain legal

## 📈 Performance Monitoring

### Dashboard Metrics

```bash
# System performance
curl "http://localhost:8000/analytics/performance"

# Compliance status
curl "http://localhost:8000/analytics/compliance"

# System status
curl "http://localhost:8000/analytics/status"
```

### Grafana Dashboard

Access comprehensive monitoring at: http://localhost:3001
- Username: admin
- Password: admin123

## 🔄 Maintenance

### Daily Operations

1. **Check System Health**: `curl http://localhost:8000/health`
2. **Review Recommendations**: Check new betting opportunities
3. **Update Bankroll**: Log any bankroll changes
4. **Log Bet Results**: Record outcomes of placed bets

### Backups

```bash
# Backup database
docker exec legal_postgres pg_dump -U sports_user sports_betting > backup.sql

# Restore database
docker exec -i legal_postgres psql -U sports_user sports_betting < backup.sql
```

## 🔧 Troubleshooting

### Common Issues

1. **No Recommendations**: Check if sports APIs are responding
2. **Low Confidence**: System only shows high-confidence picks (>70%)
3. **API Errors**: Verify OpenAI API key is configured correctly

### Logs

```bash
# View application logs
docker-compose -f docker-compose.legal.yml logs legal-betting-api

# View all logs
docker-compose -f docker-compose.legal.yml logs
```

## 🎯 Next Steps

1. **Deploy to Cloud**: Use AWS ECS, Google Cloud Run, or similar
2. **Add More Sports**: Extend to NFL, MLB, NHL
3. **Enhanced Analytics**: Add more detailed performance metrics
4. **Mobile App**: Build mobile interface for recommendations

## ⚖️ Legal Disclaimer

This system provides betting analysis and recommendations only. Users are responsible for:

- Complying with local gambling laws
- Manually placing all bets through official channels
- Managing their own bankroll responsibly
- Understanding that all gambling involves risk

No automated betting is performed by this system. All betting decisions and executions are the user's responsibility.

---

**🎯 Ready to start?** Run `docker-compose -f docker-compose.legal.yml up -d` to launch your legal betting analysis platform!