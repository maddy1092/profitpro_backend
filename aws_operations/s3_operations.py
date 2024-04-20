import boto3
import os

from botocore.exceptions import NoCredentialsError, ClientError


class AWSClientManager:
  def __init__(self, service_name, region_name, aws_access_key_id, aws_secret_access_key, bucket_name=None):
    self.service_name = service_name
    self.region_name = region_name
    self.aws_access_key_id = aws_access_key_id
    self.aws_secret_access_key = aws_secret_access_key
    self.bucket_name = bucket_name or os.environ.get("AWS_STORAGE_BUCKET_NAME")
    self.ttl = os.environ.get("AWS_S3_URL_TTL")
    self.client = self.create_client()

  def create_client(self):
    try:
      client = boto3.client(
        service_name=self.service_name,
        region_name=self.region_name,
        aws_access_key_id=self.aws_access_key_id,
        aws_secret_access_key=self.aws_secret_access_key
      )
      return client
    except NoCredentialsError as err:
      raise Exception("Error creating AWS client: {}".format(err))

  def upload_audio(self, filename, audio_file):
    try:
      self.client.put_object(
        Bucket=self.bucket_name,
        Key=filename,
        Body=audio_file,
      )
      
      aws_custom_domain = os.environ.get("AWS_S3_CUSTOM_DOMAIN")
      url = f"https://{aws_custom_domain}/{filename}"
      
      return url
    except ClientError as e:
      raise Exception("Error uploading audio to AWS: {}".format(e))

  def generate_presigned_url(self, filename):
    try:
      presigned_url = self.client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": self.bucket_name,
            "Key": filename
        },
        ExpiresIn=self.ttl
      )
      
      return presigned_url
    except ClientError as e:
      raise Exception("Error generating presigned URL: {}".format(e))

