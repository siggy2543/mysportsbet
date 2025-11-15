# 🚀 Sports Betting Automation System - Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ **System Architecture Complete**
- [x] ESPN API Integration (Modern Zuplo OpenAPI spec)
- [x] OpenAI GPT-4 Prediction Service
- [x] DraftKings Betting Automation
- [x] Master Orchestrator Service
- [x] FastAPI Routes Integration
- [x] Terraform AWS Infrastructure
- [x] Docker Configuration
- [x] Environment Variables Setup
- [x] Integration Test Framework

### 🔧 **Required Setup Steps**

#### 1. API Keys and Credentials Setup
Before deployment, you need to obtain and configure these API keys:

```bash
# 1. OpenAI API Key
# Visit: https://platform.openai.com/api-keys
# Set: OPENAI_API_KEY=sk-...

# 2. ESPN API Access
# Visit: https://developer.espn.com/
# Set: ESPN_API_KEY=your_espn_key

# 3. DraftKings Credentials
# Use your DraftKings account credentials
# Set: DRAFTKINGS_USERNAME=your_username
# Set: DRAFTKINGS_PASSWORD=your_password
# Set: DRAFTKINGS_STATE=your_state_code

# 4. AWS Credentials
# Configure AWS CLI or set environment variables
# Set: AWS_ACCESS_KEY_ID=your_access_key
# Set: AWS_SECRET_ACCESS_KEY=your_secret_key
```

#### 2. Local Development Testing

```bash
# 1. Install Dependencies
cd backend
pip install -r requirements-prod.txt

# 2. Set up Environment Variables
cp .env.example .env
# Edit .env with your actual API keys

# 3. Start Local Services
docker-compose up -d postgres redis

# 4. Run Application
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 5. Test API Endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/betting-automation/opportunities
```

#### 3. AWS Infrastructure Deployment

```bash
# 1. Initialize Terraform
cd terraform
terraform init

# 2. Plan Deployment
terraform plan -var="aws_region=us-east-1"

# 3. Deploy Infrastructure
terraform apply

# 4. Get Deployment Outputs
terraform output application_url
terraform output database_endpoint
terraform output redis_endpoint
```

#### 4. Docker Container Deployment

```bash
# 1. Build and Deploy with Docker Compose
docker-compose up --build -d

# 2. Check Container Status
docker-compose ps

# 3. View Logs
docker-compose logs -f api

# 4. Test Deployed Application
curl http://localhost/health
```

## 🏗️ **Deployment Options**

### Option 1: AWS ECS Deployment (Recommended)
- **Pros**: Auto-scaling, managed infrastructure, high availability
- **Cons**: Higher cost, complexity
- **Use Case**: Production environment with high traffic

### Option 2: Docker Compose Deployment
- **Pros**: Simple setup, cost-effective
- **Cons**: Single point of failure, manual scaling
- **Use Case**: Development, testing, small-scale production

### Option 3: Local Development
- **Pros**: Full control, no cloud costs
- **Cons**: Limited scalability, requires manual management
- **Use Case**: Development and testing

## 🔐 **Security Configuration**

### Environment Variables Security
```bash
# Use AWS Secrets Manager for production
aws secretsmanager create-secret --name sports-app-openai-key --secret-string "your_openai_key"
aws secretsmanager create-secret --name sports-app-draftkings-creds --secret-string '{"username":"user","password":"pass"}'
aws secretsmanager create-secret --name sports-app-jwt-secret --secret-string "your_jwt_secret"
```

### Database Security
- Enable SSL connections
- Use strong passwords
- Configure security groups
- Enable backup and encryption

### API Security
- Configure CORS properly
- Implement rate limiting
- Use HTTPS in production
- Validate all inputs

## 📊 **Monitoring and Alerting**

### Application Monitoring
```python
# Health Check Endpoints
GET /health                           # Basic health check
GET /api/v1/betting-automation/sessions/{id}  # Session monitoring
GET /api/v1/betting-automation/performance    # Performance metrics
```

### AWS CloudWatch
- ECS task monitoring
- RDS performance metrics
- Application logs
- Custom metrics for betting performance

### Alert Configuration
```bash
# Create CloudWatch Alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "High-Error-Rate" \
  --alarm-description "High error rate in sports betting app" \
  --metric-name ErrorRate \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 5.0 \
  --comparison-operator GreaterThanThreshold
```

## 🎯 **Testing and Validation**

### Pre-Deployment Tests
1. **Unit Tests**: Test individual service components
2. **Integration Tests**: Test complete workflow
3. **Load Tests**: Verify performance under load
4. **Security Tests**: Validate authentication and authorization

### Post-Deployment Validation
```bash
# 1. Health Checks
curl https://your-app-url/health

# 2. API Functionality
curl -X POST https://your-app-url/api/v1/betting-automation/execute-workflow \
  -H "Content-Type: application/json" \
  -d '{"sports": ["nfl"], "max_bets": 1, "risk_level": "low"}'

# 3. Database Connectivity
curl https://your-app-url/api/v1/sports/nfl/games

# 4. Cache Performance
curl https://your-app-url/api/v1/predictions/analyze
```

## 🚨 **Risk Management**

### Financial Controls
- **Maximum Single Bet**: $100 (configurable)
- **Daily Exposure Limit**: $500 (configurable)
- **Minimum Confidence**: 70% (configurable)
- **Bankroll Protection**: Never risk more than 10% per day

### Emergency Procedures
```python
# Emergency Stop All Betting
POST /api/v1/betting-automation/emergency-stop

# Pause Specific Session
POST /api/v1/betting-automation/sessions/{id}/pause

# View Real-time Performance
GET /api/v1/betting-automation/performance
```

### Backup and Recovery
- Daily database backups
- Configuration backups
- Session state persistence
- Betting history retention

## 📈 **Performance Optimization**

### Caching Strategy
- ESPN data: 1 hour cache
- Predictions: 2 hour cache
- DraftKings odds: 5 minute cache
- User sessions: 24 hour cache

### Database Optimization
- Index betting tables
- Optimize prediction queries
- Regular maintenance
- Connection pooling

### Scaling Considerations
- Horizontal scaling with ECS
- Read replicas for databases
- CDN for static content
- Load balancing

## 🔄 **Continuous Integration/Deployment**

### GitHub Actions Workflow
```yaml
name: Deploy Sports Betting App
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
      - name: Deploy to ECS
        run: |
          terraform init
          terraform apply -auto-approve
```

### Blue-Green Deployment
- Deploy to staging environment
- Run integration tests
- Switch traffic to new version
- Rollback if issues detected

## 📞 **Support and Maintenance**

### Monitoring Dashboards
- Application performance metrics
- Betting success rates
- API response times
- Error rates and alerts

### Regular Maintenance Tasks
- Update dependencies monthly
- Review betting performance weekly
- Monitor API usage limits
- Backup verification

### Troubleshooting Common Issues

#### Issue: High API Response Times
**Solution**: Check ESPN/OpenAI API status, verify network connectivity, review cache configuration

#### Issue: Betting Failures
**Solution**: Verify DraftKings credentials, check account balance, review bet validation logic

#### Issue: Database Connection Errors
**Solution**: Check RDS status, verify security groups, review connection pool settings

#### Issue: Memory/CPU Issues
**Solution**: Review ECS task sizing, optimize queries, check for memory leaks

## 🎉 **Ready for Production**

Your sports betting automation system is now ready for deployment with:

✅ **Complete ESPN API Integration**
✅ **AI-Powered Predictions**
✅ **Automated DraftKings Betting**
✅ **Risk Management Controls**
✅ **AWS Cloud Infrastructure**
✅ **Monitoring and Alerting**
✅ **Security Best Practices**
✅ **Scalable Architecture**

## 📚 **Next Steps**

1. **Configure API Keys**: Set up all required API credentials
2. **Deploy Infrastructure**: Run Terraform to create AWS resources
3. **Test System**: Verify all components work together
4. **Start Small**: Begin with small bet amounts to validate system
5. **Monitor Performance**: Track success rates and adjust strategies
6. **Scale Gradually**: Increase bet sizes as confidence grows

---

**⚠️ Important Disclaimer**: This is an automated betting system. Always gamble responsibly, understand the risks involved, and never bet more than you can afford to lose. The system is for educational and research purposes.