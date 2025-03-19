# Bills of lading, PODs and rate confirmations uploaded by shippers/drivers.
resource "aws_s3_bucket" "bol_documents" {
  bucket = "hbl-staging-bol-documents"
}

resource "aws_s3_bucket_versioning" "bol_documents" {
  bucket = aws_s3_bucket.bol_documents.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bol_documents" {
  bucket = aws_s3_bucket.bol_documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "bol_documents" {
  bucket                  = aws_s3_bucket.bol_documents.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "bol_documents" {
  bucket = aws_s3_bucket.bol_documents.id

  rule {
    id     = "expire-staging-uploads"
    status = "Enabled"

    filter {}

    # Staging only: documents are synthetic test uploads, keep 90 days.
    expiration {
      days = 90
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}
