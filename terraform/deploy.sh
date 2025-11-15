#!/bin/bash
# Sports App Terraform Deployment Script

set -e  # Exit on any error

echo "🚀 Sports Betting App - Terraform Deployment"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "main.tf" ]; then
    echo "❌ Error: main.tf not found. Please run this script from the terraform/ directory"
    exit 1
fi

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "❌ Error: terraform.tfvars not found!"
    echo "Please edit terraform.tfvars with your actual credentials:"
    echo "  - database_password"
    echo "  - openai_api_key" 
    echo "  - draftkings_username"
    echo "  - draftkings_password"
    exit 1
fi

# Validate terraform.tfvars has real values
if grep -q "your-openai-api-key-here\|your-draftkings-username\|YourSecurePassword123!" terraform.tfvars; then
    echo "❌ Error: Please update terraform.tfvars with your actual credentials!"
    echo "Found placeholder values that need to be replaced:"
    grep -n "your-openai-api-key-here\|your-draftkings-username\|YourSecurePassword123!" terraform.tfvars || true
    exit 1
fi

echo "📋 Pre-deployment checks..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run: aws configure"
    exit 1
fi

echo "✅ AWS CLI configured"

# Check Terraform version
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not installed. Please install Terraform first."
    exit 1
fi

TERRAFORM_VERSION=$(terraform version -json | jq -r '.terraform_version')
echo "✅ Terraform version: $TERRAFORM_VERSION"

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Validate configuration
echo "🔍 Validating Terraform configuration..."
terraform validate

# Format check
echo "📝 Checking Terraform formatting..."
terraform fmt -check || {
    echo "⚠️  Formatting issues found. Auto-fixing..."
    terraform fmt -recursive
}

# Plan deployment
echo "📊 Creating deployment plan..."
terraform plan -out=tfplan

# Ask for confirmation
echo ""
echo "🎯 Ready to deploy! This will create:"
echo "  - VPC with public/private subnets"
echo "  - ECS Fargate cluster for the application"
echo "  - RDS PostgreSQL database"
echo "  - ElastiCache Redis cluster"
echo "  - Application Load Balancer"
echo "  - Security groups and IAM roles"
echo ""

read -p "Do you want to proceed with deployment? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Apply the plan
echo "🚀 Deploying infrastructure..."
terraform apply tfplan

# Show outputs
echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Important Information:"
terraform output

echo ""
echo "🎉 Your Sports Betting App infrastructure is ready!"
echo ""
echo "Next steps:"
echo "1. Update your application's environment variables with the database endpoint"
echo "2. Build and push your Docker images to ECR"
echo "3. Deploy your application to ECS"
echo ""
echo "Useful commands:"
echo "  terraform output                    # Show all outputs"
echo "  terraform output database_endpoint  # Show database endpoint"
echo "  terraform destroy                   # Destroy all resources (careful!)"