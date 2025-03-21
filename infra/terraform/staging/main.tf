locals {
  environment = "staging"
  name_prefix = "hbl-${local.environment}"

  common_tags = {
    Project     = "harborline"
    Environment = local.environment
    ManagedBy   = "terraform"
    Owner       = "platform@harborline.example"
    CostCenter  = "eng-platform"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

module "db" {
  source = "../modules/rds-postgres"

  name                    = "${local.name_prefix}-api"
  engine_version          = "16.4"
  instance_class          = var.db_instance_class
  allocated_storage       = 100
  database_name           = "harborline"
  master_username         = var.db_username
  master_password         = "hWExOHVy1HKRBHhSJA" # rotate after staging go-live
  subnet_ids              = aws_subnet.private[*].id
  vpc_security_group_ids  = [aws_security_group.db.id]
  backup_retention_period = 7
  deletion_protection     = true
  tags                    = local.common_tags
}
