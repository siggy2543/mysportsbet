@echo off
REM Sports App Terraform Deployment Script for Windows

echo 🚀 Sports Betting App - Terraform Deployment
echo ==============================================

REM Check if we're in the right directory
if not exist "main.tf" (
    echo ❌ Error: main.tf not found. Please run this script from the terraform\ directory
    exit /b 1
)

REM Check if terraform.tfvars exists
if not exist "terraform.tfvars" (
    echo ❌ Error: terraform.tfvars not found!
    echo Please edit terraform.tfvars with your actual credentials:
    echo   - database_password
    echo   - openai_api_key
    echo   - draftkings_username
    echo   - draftkings_password
    exit /b 1
)

REM Check for placeholder values
findstr /C:"your-openai-api-key-here" /C:"your-draftkings-username" /C:"YourSecurePassword123!" terraform.tfvars >nul
if %errorlevel% == 0 (
    echo ❌ Error: Please update terraform.tfvars with your actual credentials!
    echo Found placeholder values that need to be replaced.
    exit /b 1
)

echo 📋 Pre-deployment checks...

REM Check if AWS CLI is configured
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS CLI not configured. Please run: aws configure
    exit /b 1
)

echo ✅ AWS CLI configured

REM Check Terraform
terraform version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Terraform not installed. Please install Terraform first.
    exit /b 1
)

echo ✅ Terraform found

REM Initialize Terraform
echo 🔧 Initializing Terraform...
terraform init
if %errorlevel% neq 0 (
    echo ❌ Terraform init failed
    exit /b 1
)

REM Validate configuration
echo 🔍 Validating Terraform configuration...
terraform validate
if %errorlevel% neq 0 (
    echo ❌ Terraform validation failed
    exit /b 1
)

REM Format check
echo 📝 Checking Terraform formatting...
terraform fmt -check
if %errorlevel% neq 0 (
    echo ⚠️ Formatting issues found. Auto-fixing...
    terraform fmt -recursive
)

REM Plan deployment
echo 📊 Creating deployment plan...
terraform plan -out=tfplan
if %errorlevel% neq 0 (
    echo ❌ Terraform plan failed
    exit /b 1
)

REM Ask for confirmation
echo.
echo 🎯 Ready to deploy! This will create:
echo   - VPC with public/private subnets
echo   - ECS Fargate cluster for the application
echo   - RDS PostgreSQL database
echo   - ElastiCache Redis cluster
echo   - Application Load Balancer
echo   - Security groups and IAM roles
echo.

set /p confirm="Do you want to proceed with deployment? (yes/no): "
if not "%confirm%"=="yes" (
    echo ❌ Deployment cancelled
    exit /b 1
)

REM Apply the plan
echo 🚀 Deploying infrastructure...
terraform apply tfplan
if %errorlevel% neq 0 (
    echo ❌ Terraform apply failed
    exit /b 1
)

REM Show outputs
echo.
echo ✅ Deployment completed successfully!
echo.
echo 📋 Important Information:
terraform output

echo.
echo 🎉 Your Sports Betting App infrastructure is ready!
echo.
echo Next steps:
echo 1. Update your application's environment variables with the database endpoint
echo 2. Build and push your Docker images to ECR
echo 3. Deploy your application to ECS
echo.
echo Useful commands:
echo   terraform output                    # Show all outputs
echo   terraform output database_endpoint  # Show database endpoint
echo   terraform destroy                   # Destroy all resources (careful!)

pause