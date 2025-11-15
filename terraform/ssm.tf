# SSM Parameters for sensitive configuration

resource "aws_ssm_parameter" "openai_api_key" {
  name  = "/${local.name_prefix}/openai/api-key"
  type  = "SecureString"
  value = var.openai_api_key

  tags = {
    Name = "${local.name_prefix}-openai-key"
  }
}

resource "aws_ssm_parameter" "draftkings_username" {
  name  = "/${local.name_prefix}/draftkings/username"
  type  = "SecureString"
  value = var.draftkings_username

  tags = {
    Name = "${local.name_prefix}-dk-username"
  }
}

resource "aws_ssm_parameter" "draftkings_password" {
  name  = "/${local.name_prefix}/draftkings/password"
  type  = "SecureString"
  value = var.draftkings_password

  tags = {
    Name = "${local.name_prefix}-dk-password"
  }
}
