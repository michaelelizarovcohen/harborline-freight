# The staging database itself is created by module "db" in main.tf.
# This file holds the supporting pieces: parameter group, alarms and the
# Secrets Manager reference that apps read the connection details from.

resource "aws_db_parameter_group" "postgres16" {
  name   = "${local.name_prefix}-pg16"
  family = "postgres16"

  parameter {
    name  = "log_min_duration_statement"
    value = "500"
  }

  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "db_cpu_high" {
  alarm_name          = "${local.name_prefix}-db-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Staging RDS CPU above 80% for 15 minutes"

  dimensions = {
    DBInstanceIdentifier = module.db.instance_id
  }
}

# Connection metadata for the API. The password itself is managed out of band
# (rotated by the hbl-secrets-rotation Lambda) and passed to Terraform via
# TF_VAR_db_password — it is never written to this repo.
resource "aws_secretsmanager_secret" "api_db" {
  name        = "hbl/staging/api-db-endpoint"
  description = "Non-secret connection metadata for the staging API database"
}

resource "aws_secretsmanager_secret_version" "api_db" {
  secret_id = aws_secretsmanager_secret.api_db.id
  secret_string = jsonencode({
    host     = module.db.address
    port     = module.db.port
    database = "harborline"
    username = var.db_username
  })
}
