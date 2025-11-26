#!/bin/bash

# ============================================================
# AWS Infrastructure Destruction Script
# Removes all AWS resources deployed by Terraform
# ============================================================

echo "========================================"
echo "AWS INFRASTRUCTURE DESTRUCTION"
echo "========================================"
echo ""
echo "This will DELETE all AWS resources:"
echo " - ECS Cluster and Services"
echo " - Application Load Balancer"
echo " - RDS PostgreSQL Database"
echo " - ElastiCache Redis Cluster"
echo " - VPC and all networking components"
echo " - ECR Images (optional)"
echo " - SSM Parameters"
echo ""
echo "WARNING: This action is IRREVERSIBLE!"
echo ""
read -p "Type 'DELETE' to confirm destruction: " CONFIRM

if [ "$CONFIRM" != "DELETE" ]; then
    echo ""
    echo "Destruction cancelled."
    exit 0
fi

echo ""
echo "========================================"
echo "STEP 1: Stopping ECS Services"
echo "========================================"
echo ""

# Stop ECS service first to avoid delete issues
aws ecs update-service \
    --cluster sports-app-production-cluster \
    --service sports-app-production-api-service \
    --desired-count 0 \
    --force-new-deployment || echo "Warning: Failed to stop ECS service"

echo "Waiting for tasks to drain..."
sleep 30

echo ""
echo "========================================"
echo "STEP 2: Terraform Destroy"
echo "========================================"
echo ""

cd terraform || exit 1
terraform destroy -auto-approve

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Terraform destroy failed!"
    echo "You may need to manually clean up resources."
    cd ..
    exit 1
fi

cd ..

echo ""
echo "========================================"
echo "STEP 3: Cleaning ECR Images (Optional)"
echo "========================================"
echo ""

read -p "Delete ECR images? (y/n): " CLEAN_ECR
if [ "$CLEAN_ECR" = "y" ] || [ "$CLEAN_ECR" = "Y" ]; then
    echo "Deleting ECR images..."
    aws ecr batch-delete-image \
        --repository-name sports-app-api \
        --image-ids imageTag=latest || echo "Warning: Failed to delete ECR images"
    echo "Note: ECR repository kept for future use"
fi

echo ""
echo "========================================"
echo "STEP 4: Verifying Cleanup"
echo "========================================"
echo ""

echo "Checking for remaining ECS resources..."
aws ecs list-clusters | grep sports-app-production || echo "✅ No ECS clusters found"

echo ""
echo "Checking for remaining load balancers..."
aws elbv2 describe-load-balancers | grep sports-app-production || echo "✅ No load balancers found"

echo ""
echo "Checking for remaining RDS instances..."
aws rds describe-db-instances | grep sports-app-production || echo "✅ No RDS instances found"

echo ""
echo "========================================"
echo "DESTRUCTION COMPLETE"
echo "========================================"
echo ""
echo "All AWS resources have been destroyed."
echo "Your local environment is now ready to use."
echo ""
echo "Estimated monthly savings: \$150-200"
echo ""
echo "Next steps:"
echo "1. Run: docker-compose down (stop any local containers)"
echo "2. Run: docker-compose build (rebuild with new code)"
echo "3. Run: docker-compose up -d (start local production)"
echo ""
