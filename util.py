import psycopg2
import json
import boto3
import os
import requests

from botocore.exceptions import ClientError

def detect_running_region():
    """Dynamically determine the region from a running Glue job (or anything on EC2 for
    that matter)."""
    easy_checks = [
        # check if set through ENV vars
        os.environ.get('AWS_REGION'),
        os.environ.get('AWS_DEFAULT_REGION'),
        # else check if set in config or in boto already
        boto3.DEFAULT_SESSION.region_name if boto3.DEFAULT_SESSION else None,
        boto3.Session().region_name,
    ]
    for region in easy_checks:
        if region:
            return region

    # else query the instance metadata service v2
    # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
    r = requests.put("http://169.254.169.254/latest/api/token", headers={"X-aws-ec2-metadata-token-ttl-seconds": "5"})
    metadata_token = r.text

    # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-identity-documents.html
    r = requests.get("http://169.254.169.254/latest/dynamic/instance-identity/document", headers={"X-aws-ec2-metadata-token": metadata_token})
    response_json = r.json()
    return response_json.get('region')

def get_secret():
    secret_name = "flasksecret"
    region_name = detect_running_region()
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            print("The requested secret can't be decrypted using the provided KMS key:", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            print("An error occurred on service side:", e)
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            text_secret_data = get_secret_value_response['SecretString']
        else:
            text_secret_data = get_secret_value_response['SecretBinary']
        return text_secret_data

def get_conn():
    conn = None
    try:
        creds = json.loads(get_secret())
    except (Exception, psycopg2.DatabaseError) as error:
        # usefull for local testing
        creds = {
            'host' : '127.0.0.1',
            'username' : 'postgres',
            'password' : ''
        }
    finally:
        conn = psycopg2.connect(
            host=creds['host'],
            database="postgres",
            user=creds['username'],
            password=creds['password']
        )
    return conn
