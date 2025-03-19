output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}

output "db_endpoint" {
  description = "Writer endpoint for the staging API database"
  value       = module.db.address
}

output "bol_bucket_name" {
  value = aws_s3_bucket.bol_documents.bucket
}
