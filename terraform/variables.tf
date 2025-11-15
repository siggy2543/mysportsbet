# Variables for the Sports Betting Application Infrastructure

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "sports-app"
}

variable "database_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key for predictions"
  type        = string
  sensitive   = true
}

variable "draftkings_username" {
  description = "DraftKings username"
  type        = string
  sensitive   = true
}

variable "draftkings_password" {
  description = "DraftKings password"
  type        = string
  sensitive   = true
}
