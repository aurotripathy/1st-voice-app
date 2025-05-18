import boto3
import os
AWS_S3_BUCKET_NAME = 'aurovoice'
AWS_REGION = 'us-east-2'

# get these from the env variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

LOCAL_FILE = 'test_file2.txt'
NAME_FOR_S3 = 'test_file2.txt'

def main():
    print('in main method')

    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    response = s3_client.upload_file(LOCAL_FILE, AWS_S3_BUCKET_NAME, NAME_FOR_S3)

    print(f'upload_log_to_aws response: {response}')

if __name__ == '__main__':
    main()