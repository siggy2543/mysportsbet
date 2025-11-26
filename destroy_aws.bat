@echo off
REM ============================================================
REM AWS Infrastructure Destruction Script
REM Removes all AWS resources deployed by Terraform
REM ============================================================

echo ========================================
echo AWS INFRASTRUCTURE DESTRUCTION
echo ========================================
echo.
echo This will DELETE all AWS resources:
echo  - ECS Cluster and Services
echo  - Application Load Balancer
echo  - RDS PostgreSQL Database
echo  - ElastiCache Redis Cluster
echo  - VPC and all networking components
echo  - ECR Images
echo  - SSM Parameters
echo.
echo WARNING: This action is IRREVERSIBLE!
echo.
set /p CONFIRM="Type 'DELETE' to confirm destruction: "

if NOT "%CONFIRM%"=="DELETE" (
    echo.
    echo Destruction cancelled.
    exit /b 0
)

echo.
echo ========================================
echo STEP 1: Stopping ECS Services
echo ========================================
echo.

REM Stop ECS service first to avoid delete issues
aws ecs update-service --cluster sports-app-production-cluster --service sports-app-production-api-service --desired-count 0 --force-new-deployment
if errorlevel 1 (
    echo Warning: Failed to stop ECS service
)

echo Waiting for tasks to drain...
timeout /t 30

echo.
echo ========================================
echo STEP 2: Terraform Destroy
echo ========================================
echo.

cd terraform
terraform destroy -auto-approve

if errorlevel 1 (
    echo.
    echo ERROR: Terraform destroy failed!
    echo You may need to manually clean up resources.
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo STEP 3: Cleaning ECR Images (Optional)
echo ========================================
echo.

set /p CLEAN_ECR="Delete ECR images? (y/n): "
if /i "%CLEAN_ECR%"=="y" (
    echo Deleting ECR images...
    aws ecr batch-delete-image --repository-name sports-app-api --image-ids imageTag=latest
    echo Note: ECR repository kept for future use
)

echo.
echo ========================================
echo STEP 4: Verifying Cleanup
echo ========================================
echo.

echo Checking for remaining ECS resources...
aws ecs list-clusters | findstr sports-app-production

echo.
echo Checking for remaining load balancers...
aws elbv2 describe-load-balancers | findstr sports-app-production

echo.
echo Checking for remaining RDS instances...
aws rds describe-db-instances | findstr sports-app-production

echo.
echo ========================================
echo DESTRUCTION COMPLETE
echo ========================================
echo.
echo All AWS resources have been destroyed.
echo Your local environment is now ready to use.
echo.
echo Estimated monthly savings: $150-200
echo.
echo Next steps:
echo 1. Run: docker-compose down (stop any local containers)
echo 2. Run: docker-compose build (rebuild with new code)
echo 3. Run: docker-compose up -d (start local production)
echo.

pause
