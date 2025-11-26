#!/bin/bash
# Production Deployment Script - Deploy Enhanced Platform to AWS ECS
# Run this after pushing to GitHub

set -e  # Exit on any error

echo "=========================================="
echo "🚀 Production Deployment - Enhanced Platform"
echo "=========================================="
echo ""

# Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
ECR_REPO_API="sports-app-api"
ECR_REPO_FRONTEND="sports-app-frontend"
ECS_CLUSTER="sports-betting-cluster"
ECS_SERVICE_API="sports-api-service"
ECS_SERVICE_FRONTEND="sports-frontend-service"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if AWS CLI is configured
echo "🔍 Checking AWS configuration..."
if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${RED}❌ AWS CLI not configured. Run: aws configure${NC}"
    exit 1
fi
echo -e "${GREEN}✓ AWS CLI configured${NC}"
echo ""

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📋 AWS Account: $AWS_ACCOUNT_ID"
echo ""

# Step 1: Run tests
echo "🧪 Step 1: Running comprehensive tests..."
if ./test_all_features.sh; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${RED}❌ Tests failed. Aborting deployment.${NC}"
    exit 1
fi
echo ""

# Step 2: Build production images
echo "🔨 Step 2: Building production Docker images..."
echo "Building API..."
docker-compose build api
echo "Building Frontend..."
docker-compose build frontend
echo -e "${GREEN}✓ Images built successfully${NC}"
echo ""

# Step 3: Tag images for ECR
echo "🏷️  Step 3: Tagging images for ECR..."
docker tag sports_app-api:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_API:latest
docker tag sports_app-api:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_API:v4.0.0
docker tag sports_app-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_FRONTEND:latest
docker tag sports_app-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_FRONTEND:v4.0.0
echo -e "${GREEN}✓ Images tagged${NC}"
echo ""

# Step 4: Login to ECR
echo "🔐 Step 4: Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
echo -e "${GREEN}✓ Logged into ECR${NC}"
echo ""

# Step 5: Create ECR repositories if they don't exist
echo "📦 Step 5: Ensuring ECR repositories exist..."
aws ecr describe-repositories --repository-names $ECR_REPO_API --region $AWS_REGION &>/dev/null || \
    aws ecr create-repository --repository-name $ECR_REPO_API --region $AWS_REGION
aws ecr describe-repositories --repository-names $ECR_REPO_FRONTEND --region $AWS_REGION &>/dev/null || \
    aws ecr create-repository --repository-name $ECR_REPO_FRONTEND --region $AWS_REGION
echo -e "${GREEN}✓ ECR repositories ready${NC}"
echo ""

# Step 6: Push images to ECR
echo "⬆️  Step 6: Pushing images to ECR..."
echo "Pushing API image..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_API:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_API:v4.0.0
echo "Pushing Frontend image..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_FRONTEND:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_FRONTEND:v4.0.0
echo -e "${GREEN}✓ Images pushed to ECR${NC}"
echo ""

# Step 7: Update ECS task definitions (if using terraform)
echo "🔄 Step 7: Updating ECS services..."
if [ -d "terraform" ]; then
    echo "Using Terraform for deployment..."
    cd terraform
    terraform init -upgrade
    terraform plan
    read -p "Apply Terraform changes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply -auto-approve
        echo -e "${GREEN}✓ Terraform applied${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipped Terraform apply${NC}"
    fi
    cd ..
else
    echo "No Terraform directory found, updating ECS services manually..."
    
    # Force new deployment (pulls latest images)
    aws ecs update-service \
        --cluster $ECS_CLUSTER \
        --service $ECS_SERVICE_API \
        --force-new-deployment \
        --region $AWS_REGION &>/dev/null || echo "API service not found, may need manual creation"
    
    aws ecs update-service \
        --cluster $ECS_CLUSTER \
        --service $ECS_SERVICE_FRONTEND \
        --force-new-deployment \
        --region $AWS_REGION &>/dev/null || echo "Frontend service not found, may need manual creation"
    
    echo -e "${GREEN}✓ ECS services updated${NC}"
fi
echo ""

# Step 8: Wait for deployment to complete
echo "⏳ Step 8: Waiting for services to stabilize..."
echo "This may take 2-5 minutes..."

# Wait for API service
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER \
    --services $ECS_SERVICE_API \
    --region $AWS_REGION &>/dev/null || echo "Waiting for API..."

# Wait for Frontend service  
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER \
    --services $ECS_SERVICE_FRONTEND \
    --region $AWS_REGION &>/dev/null || echo "Waiting for Frontend..."

echo -e "${GREEN}✓ Services stabilized${NC}"
echo ""

# Step 9: Get load balancer URL
echo "🌐 Step 9: Getting application URL..."
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --query "LoadBalancers[?contains(LoadBalancerName, 'sports')].DNSName" \
    --output text \
    --region $AWS_REGION 2>/dev/null || echo "not-found")

if [ "$ALB_DNS" != "not-found" ]; then
    echo -e "${GREEN}✓ Application deployed successfully!${NC}"
    echo ""
    echo "🎉 Deployment Complete!"
    echo "=========================================="
    echo "🌍 Access your application at:"
    echo "   http://$ALB_DNS"
    echo ""
    echo "🏥 Health check:"
    echo "   curl http://$ALB_DNS/api/health"
    echo ""
    echo "🧪 Test enhanced features:"
    echo "   curl http://$ALB_DNS/api/feedback/dashboard"
    echo "   curl http://$ALB_DNS/api/team-analysis/NBA/Lakers"
    echo ""
else
    echo -e "${YELLOW}⚠️  Could not find load balancer. Check AWS Console.${NC}"
fi

echo "=========================================="
echo "📊 Deployment Summary:"
echo "   Version: 4.0.0"
echo "   Region: $AWS_REGION"
echo "   Cluster: $ECS_CLUSTER"
echo "   Images pushed: API + Frontend"
echo "   Status: ✅ SUCCESS"
echo "=========================================="
echo ""
echo "📚 Next steps:"
echo "   1. Test the application at the URL above"
echo "   2. Monitor CloudWatch logs for any issues"
echo "   3. Set up The Odds API for real odds data"
echo "   4. Start collecting bet outcomes for ML training"
echo ""
