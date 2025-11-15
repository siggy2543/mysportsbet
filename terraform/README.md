# Terraform Deployment Fix & Setup Guide

## 🚨 Error Resolution: "No configuration files"

The error occurs when running `terraform apply` from the wrong directory or missing required files.

## ✅ Quick Fix Steps

### 1. Navigate to the Correct Directory
```bash
cd c:\Users\cigba\sports_app\terraform
```

### 2. Update terraform.tfvars with Your Credentials
Edit `terraform.tfvars` and replace the placeholder values:

```hcl
# Replace these with your actual values:
database_password = "YourActualSecurePassword123!"
openai_api_key = "sk-your-actual-openai-key"
draftkings_username = "your-actual-username"
draftkings_password = "your-actual-password"
```

⚠️ **IMPORTANT**: Never commit `terraform.tfvars` to version control!

### 3. Ensure AWS CLI is Configured
```bash
aws configure
```
You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)

### 4. Deploy Using the Script (Recommended)
```bash
# Windows
.\deploy.bat

# Linux/Mac/WSL
chmod +x deploy.sh
./deploy.sh
```

### 5. Manual Deployment (Alternative)
```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Create deployment plan
terraform plan

# Apply (deploy) the infrastructure
terraform apply
```

## 📋 Prerequisites Checklist

- [ ] AWS CLI installed and configured
- [ ] Terraform installed (version >= 1.0)
- [ ] Valid AWS credentials with sufficient permissions
- [ ] Updated `terraform.tfvars` with real credentials
- [ ] Running from the `terraform/` directory

## 🔧 Common Issues & Solutions

### Issue: "AWS credentials not found"
**Solution**: Run `aws configure` and provide your AWS credentials

### Issue: "Invalid provider registry"
**Solution**: Run `terraform init` to download required providers

### Issue: "Validation failed"
**Solution**: Check `terraform.tfvars` for missing or invalid values

### Issue: "Permission denied"
**Solution**: Ensure your AWS user has sufficient IAM permissions

## 🎯 What Gets Deployed

Your Terraform configuration will create:

1. **VPC & Networking**
   - Virtual Private Cloud with public/private subnets
   - Internet Gateway and NAT Gateways
   - Route tables and security groups

2. **Compute Resources**
   - ECS Fargate cluster for containerized apps
   - Application Load Balancer
   - Auto-scaling policies

3. **Database & Caching**
   - RDS PostgreSQL database
   - ElastiCache Redis cluster
   - Database subnet groups

4. **Security & Monitoring**
   - IAM roles and policies
   - Security groups with least privilege
   - CloudWatch logging

## 💰 Cost Estimation

Approximate monthly costs (us-east-1):
- RDS PostgreSQL (db.t3.micro): ~$15
- ElastiCache Redis (cache.t3.micro): ~$12
- ECS Fargate (minimal usage): ~$5-20
- Load Balancer: ~$18
- NAT Gateway: ~$32
- **Total: ~$82-97/month**

## 🧹 Cleanup

To destroy all resources:
```bash
terraform destroy
```

⚠️ **WARNING**: This will delete ALL resources and data!

## 📞 Support

If you encounter issues:
1. Check the Terraform error messages carefully
2. Ensure all prerequisites are met
3. Verify your AWS credentials and permissions
4. Make sure you're in the correct directory

## 🎉 Success!

After successful deployment, you'll see outputs with:
- Database endpoint
- Load balancer DNS name
- VPC details
- Other important resource information

Use these outputs to configure your application's environment variables.