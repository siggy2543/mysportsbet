# 🚀 Deployment Guide

This guide provides step-by-step instructions for deploying the Sports Betting Platform to AWS and setting it up for production use.

## 📋 Prerequisites

### Required Tools
- **AWS CLI**: Version 2.x or higher
- **Docker**: Version 20.x or higher
- **Docker Compose**: Version 2.x or higher
- **Git**: For version control
- **Bash/PowerShell**: For running deployment scripts

### AWS Requirements
- AWS Account with appropriate permissions
- IAM user with the following permissions:
  - CloudFormation (Full Access)
  - ECS (Full Access)
  - ECR (Full Access)
  - RDS (Full Access)
  - ElastiCache (Full Access)
  - VPC (Full Access)
  - IAM (Limited - for role creation)
  - Secrets Manager (Full Access)

### API Keys Required
- ESPN API Key
- RapidAPI Key (for The Rundown and All-Sports)
- DraftKings API Key (for bet placement)

## 🔧 Local Development Setup

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/siggy2543/mysportsbet.git
cd sports_app

# Copy environment template
cp variables.env .env

# Edit configuration
nano .env
```

### 2. Environment Configuration

Update `.env` with your values:

```env
# Database Configuration
DATABASE_URL=postgresql://sports_user:sports_pass@localhost:5432/sports_betting
REDIS_URL=redis://localhost:6379

# API Keys
ESPN_API_KEY=your_espn_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
DRAFTKINGS_API_KEY=your_draftkings_api_key_here
THE_RUNDOWN_API_KEY=your_rundown_api_key_here

# Security
SECRET_KEY=your-super-secret-jwt-key-min-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
MAX_BET_AMOUNT=1000.0
MIN_BET_AMOUNT=10.0
BANKROLL_PERCENTAGE_LIMIT=0.05

# CORS Settings
ALLOWED_HOSTS=http://localhost:3000,https://yourdomain.com
```

### 3. Start Local Development

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
```

### 4. Verify Installation

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database: localhost:5432
- Redis: localhost:6379

## ☁️ AWS Deployment

### Step 1: Prepare AWS Environment

1. **Configure AWS CLI**
```bash
aws configure
# Enter your Access Key ID, Secret Access Key, and default region
```

2. **Create Secrets in AWS Secrets Manager**
```bash
# Database password
aws secretsmanager create-secret \
    --name "sports-betting-db-password" \
    --description "Database password for Sports Betting App" \
    --secret-string '{"password":"your-secure-db-password"}'

# API Keys
aws secretsmanager create-secret \
    --name "sports-betting-api-keys" \
    --description "API keys for Sports Betting App" \
    --secret-string '{
        "ESPN_API_KEY":"your-espn-key",
        "RAPIDAPI_KEY":"your-rapidapi-key",
        "DRAFTKINGS_API_KEY":"your-draftkings-key",
        "THE_RUNDOWN_API_KEY":"your-rundown-key"
    }'
```

### Step 2: Automated Deployment

```bash
# Make deployment script executable
chmod +x deploy-aws.sh

# Run deployment
./deploy-aws.sh
```

### Step 3: Manual Deployment (Alternative)

If the automated script fails, follow these manual steps:

1. **Deploy Infrastructure**
```bash
aws cloudformation deploy \
    --template-file aws/infrastructure.yml \
    --stack-name sports-betting-infrastructure \
    --capabilities CAPABILITY_IAM \
    --region us-east-1
```

2. **Build and Push Docker Images**
```bash
# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1

# Login to ECR
aws ecr get-login-password --region $REGION | \
    docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build backend image
cd backend
docker build -t sports-betting-backend .
docker tag sports-betting-backend:latest \
    $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/sports-betting-backend:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/sports-betting-backend:latest

# Build frontend image
cd ../frontend
docker build -t sports-betting-frontend .
docker tag sports-betting-frontend:latest \
    $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/sports-betting-frontend:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/sports-betting-frontend:latest
```

3. **Deploy ECS Services**
```bash
aws cloudformation deploy \
    --template-file aws/ecs-services.yml \
    --stack-name sports-betting-services \
    --capabilities CAPABILITY_IAM \
    --region us-east-1 \
    --parameter-overrides \
        InfrastructureStackName=sports-betting-infrastructure \
        BackendImageUri=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/sports-betting-backend:latest \
        FrontendImageUri=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/sports-betting-frontend:latest
```

### Step 4: Post-Deployment Configuration

1. **Get Application URLs**
```bash
# Get Load Balancer DNS
aws cloudformation describe-stacks \
    --stack-name sports-betting-infrastructure \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text
```

2. **Run Database Migrations**
```bash
# Connect to ECS task and run migrations
aws ecs run-task \
    --cluster sports-betting-cluster \
    --task-definition sports-betting-backend \
    --overrides '{
        "containerOverrides": [{
            "name": "backend",
            "command": ["alembic", "upgrade", "head"]
        }]
    }'
```

3. **Verify Deployment**
- Check ECS service status in AWS Console
- Test API endpoints
- Verify database connectivity
- Check application logs

## 🔒 Security Configuration

### SSL Certificate Setup

1. **Request Certificate via ACM**
```bash
aws acm request-certificate \
    --domain-name yourdomain.com \
    --validation-method DNS \
    --subject-alternative-names *.yourdomain.com
```

2. **Update Load Balancer**
- Add HTTPS listener
- Configure SSL certificate
- Set up HTTP to HTTPS redirect

### Environment Variables

Update ECS task definitions with production values:

```json
{
    "environment": [
        {"name": "DEBUG", "value": "False"},
        {"name": "LOG_LEVEL", "value": "INFO"},
        {"name": "DATABASE_URL", "value": "postgresql://..."}
    ],
    "secrets": [
        {
            "name": "SECRET_KEY",
            "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:sports-betting-keys-AbCdEf"
        }
    ]
}
```

## 📊 Monitoring Setup

### CloudWatch Configuration

1. **Set up Log Groups**
```bash
aws logs create-log-group --log-group-name /ecs/sports-betting-backend
aws logs create-log-group --log-group-name /ecs/sports-betting-frontend
```

2. **Configure Alarms**
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "sports-betting-high-error-rate" \
    --alarm-description "High error rate detected" \
    --metric-name ErrorRate \
    --namespace AWS/ApplicationELB \
    --statistic Average \
    --period 300 \
    --threshold 5.0 \
    --comparison-operator GreaterThanThreshold
```

### Application Metrics

The backend includes Prometheus metrics on `/metrics` endpoint:
- Request count and duration
- Database connection pool status
- Cache hit/miss rates
- Custom business metrics

## 🔄 CI/CD Pipeline

### GitHub Actions Setup

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy to AWS
        run: ./deploy-aws.sh
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Issues**
```bash
# Check RDS status
aws rds describe-db-instances --db-instance-identifier sports-betting-db

# Verify security groups
aws ec2 describe-security-groups --group-names sports-betting-rds-sg
```

2. **ECS Task Failures**
```bash
# Check task status
aws ecs describe-tasks --cluster sports-betting-cluster --tasks <task-arn>

# View logs
aws logs get-log-events --log-group-name /ecs/sports-betting-backend --log-stream-name <stream-name>
```

3. **Load Balancer Issues**
```bash
# Check target health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
```

### Performance Optimization

1. **Enable Auto Scaling**
```bash
# Create auto scaling target
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/sports-betting-cluster/backend-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 2 \
    --max-capacity 10
```

2. **Configure CloudFront CDN**
```bash
# Create CloudFront distribution for static assets
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json
```

## 📈 Scaling Considerations

### Horizontal Scaling
- ECS Auto Scaling based on CPU/memory
- Database read replicas for read-heavy workloads
- ElastiCache cluster mode for Redis scaling

### Vertical Scaling
- Upgrade RDS instance class
- Increase ECS task CPU/memory
- Optimize application code and queries

## 🔐 Backup and Recovery

### Database Backups
- Automated RDS backups (7-day retention)
- Manual snapshots before deployments
- Cross-region backup replication

### Application State
- Store configuration in version control
- Use Infrastructure as Code (CloudFormation)
- Regular disaster recovery testing

---

For additional support, consult the [AWS Documentation](https://docs.aws.amazon.com/) or create an issue in the project repository.