import os
import boto3

from dotenv import load_dotenv

from src.constants import (
    AWS_SECRET_ACCESS_KEY_ENV_KEY,
    AWS_ACCESS_KEY_ID_ENV_KEY,
    REGION_NAME
)


# Load .env from project root
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)


class S3Client:

    s3_client = None
    s3_resource = None

    def __init__(self, region_name=REGION_NAME):

        """
        Creates AWS S3 client using credentials from .env
        """

        if S3Client.s3_resource is None or S3Client.s3_client is None:

            access_key_id = os.getenv(
                AWS_ACCESS_KEY_ID_ENV_KEY
            )

            secret_access_key = os.getenv(
                AWS_SECRET_ACCESS_KEY_ENV_KEY
            )

            if not access_key_id:
                raise Exception(
                    f"Environment variable "
                    f"{AWS_ACCESS_KEY_ID_ENV_KEY} is not set."
                )

            if not secret_access_key:
                raise Exception(
                    f"Environment variable "
                    f"{AWS_SECRET_ACCESS_KEY_ENV_KEY} is not set."
                )

            print(f"AWS region: {region_name}")
            print(f"AWS access key loaded: {access_key_id[:4]}****")

            S3Client.s3_resource = boto3.resource(
                "s3",
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region_name
            )

            S3Client.s3_client = boto3.client(
                "s3",
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region_name
            )

        self.s3_resource = S3Client.s3_resource
        self.s3_client = S3Client.s3_client