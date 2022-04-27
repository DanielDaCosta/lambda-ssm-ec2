import boto3
import logging
from config import \
    INSTANCE_NAME, \
    SNS_ROLE, \
    SNS_ARN, \
    BUCKET_NAME
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    
    FILE_NAME = "restore_db.sh"

    # boto3 client
    client = boto3.client("ec2")
    ssm = boto3.client("ssm")

    # getting instance information
    describeInstance = client.describe_instances(
        Filters=[{
            'Name': 'tag:Name',
            'Values': [INSTANCE_NAME]
        }]
    )
    
    # Check if Instance is Running
    InstanceId = []
    for i in describeInstance["Reservations"]:
        for instance in i["Instances"]:
            if instance["State"]["Name"] == "running":
                InstanceId.append(instance["InstanceId"])
    logger.info(f"Instance-id: {InstanceId}" )
    
    if not len(InstanceId):
        logger.error("No Instance in Running state were found")
        raise Exception("No Instance in Running state were found")
    
    print(f"Executing command on instance: {InstanceId}")
    # looping through instance ids
    for instanceid in InstanceId:
        # command to be executed on instance
        response = ssm.send_command(
            InstanceIds=[instanceid],
            DocumentName="AWS-RunRemoteScript",
            Parameters={
                "sourceType": ["S3"],
                "sourceInfo": ["{\"path\":\"" + f"https://s3.amazonaws.com/{BUCKET_NAME}/data-ingestion/{FILE_NAME}" + "\"}"],
                "commandLine": [f"{FILE_NAME}"]
            },  # replace command_to_be_executed with command
            Comment="Execute ods database restore",
            ServiceRoleArn=SNS_ROLE,
            NotificationConfig={
                "NotificationArn": SNS_ARN,
                "NotificationEvents": ["Success"],
                "NotificationType": "Command"
            },
            OutputS3Region='us-east-1',
            OutputS3BucketName=BUCKET_NAME,
            OutputS3KeyPrefix='data-ingestion/logs_ssm',
        )

        # fetching command id for the output
        command_id = response["Command"]["CommandId"]
        logger.info(f"Command Id: {command_id}")
        

    return {"statusCode": 200, "command_id": command_id}