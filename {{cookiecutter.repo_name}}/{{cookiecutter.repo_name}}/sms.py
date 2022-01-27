import boto3
from decouple import config

client = boto3.client(
    "sns",
    aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
    region_name=config('REGION_NAME')
)


def send_otp(phone, otp):
    client.publish(
        PhoneNumber=phone,
        Message=f"{otp} is your Spacium verification code."
    )
