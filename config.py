from os import getenv

# Lambda ENV Variables
INSTANCE_NAME   = getenv('INSTANCE_NAME')
SNS_ROLE        = getenv('SNS_ROLE')
SNS_ARN         = getenv('SNS_ARN')
BUCKET_NAME     = getenv('BUCKET_NAME')
