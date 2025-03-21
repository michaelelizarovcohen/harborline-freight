variable "aws_region" {
  description = "AWS region for the staging environment"
  type        = string
  default     = "us-west-2"
}

variable "staging_account_id" {
  description = "AWS account ID of harborline-staging (looked up from the org, not secret)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the staging VPC"
  type        = string
  default     = "10.40.0.0/16"
}

variable "db_instance_class" {
  description = "RDS instance class for the staging API database"
  type        = string
  default     = "db.t4g.medium"
}

variable "db_username" {
  description = "Master username for the staging API database"
  type        = string
  default     = "hbl_admin"
}

variable "db_password" {
  description = "Master password for the staging API database. Supply via TF_VAR_db_password."
  type        = string
  sensitive   = true
}
