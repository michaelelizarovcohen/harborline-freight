# Staging bastion

The staging database is only reachable from inside the VPC. To run ad-hoc
queries, open a tunnel through the SSM-managed bastion:

```bash
aws sso login --profile hbl-shared
export AWS_PROFILE=hbl-shared
./deploy/bastion/tunnel.sh 15432
psql "host=localhost port=15432 dbname=harborline user=$USER sslmode=require"
```

History note: until mid-2025 this folder briefly held an SSH key for an EC2
jump host. That host is gone, the key was revoked, and SSH ingress is closed
(`aws_security_group.bastion` has no inbound rules). Please don't add keys here.
