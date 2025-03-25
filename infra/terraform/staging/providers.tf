terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "s3" {
    bucket         = "hbl-terraform-state-staging"
    key            = "staging/core.tfstate"
    region         = "us-west-2"
    dynamodb_table = "hbl-terraform-locks"
    encrypt        = true
  }
}

# Credentials come from the caller's SSO session (AWS_PROFILE=hbl-shared).
# Do NOT add access_key / secret_key here — see infra/README.md.
provider "aws" {
  region = var.aws_region

  assume_role {
    role_arn     = "arn:aws:iam::${var.staging_account_id}:role/TerraformDeployer"
    session_name = "terraform-staging"
  }

  default_tags {
    tags = local.common_tags
  }
}
