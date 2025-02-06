"""S3 storage for bills of lading (BOL) and proof-of-delivery photos.

Credentials come from the default boto3 chain (IRSA in EKS, `aws sso login`
locally). Do not pass access keys explicitly.
"""
import logging
import uuid
from datetime import datetime, timezone

from flask import current_app

log = logging.getLogger("harborline.storage")

ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/heic"}


def _client():
    import boto3  # lazy: tests don't need boto3

    return boto3.client("s3", region_name=current_app.config["AWS_REGION"])


def _key(prefix: str, reference: str, filename: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"{prefix}/{today}/{reference}/{uuid.uuid4().hex}.{ext}"


def upload_bol(reference: str, fileobj, filename: str, content_type: str) -> str:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"unsupported content type {content_type}")
    key = _key("bol", reference, filename)
    _client().upload_fileobj(
        fileobj,
        current_app.config["BOL_BUCKET"],
        key,
        ExtraArgs={"ContentType": content_type, "ServerSideEncryption": "aws:kms"},
    )
    log.info("uploaded BOL for %s to s3://%s/%s", reference, current_app.config["BOL_BUCKET"], key)
    return key


def upload_pod_photo(tracking_number: str, fileobj, filename: str, content_type: str) -> str:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"unsupported content type {content_type}")
    key = _key("pod", tracking_number, filename)
    _client().upload_fileobj(
        fileobj, current_app.config["POD_BUCKET"], key,
        ExtraArgs={"ContentType": content_type, "ServerSideEncryption": "aws:kms"},
    )
    return key


def presigned_url(bucket: str, key: str, expires: int = 900) -> str:
    return _client().generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expires
    )
