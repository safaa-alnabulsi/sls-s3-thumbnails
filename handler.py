import json
import boto3
import logging
from botocore.exceptions import ClientError
from PIL import Image
import glob, os

size = 2, 2
prefix = 'thumbnail_'

def s3_generate_thumbnails(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    if not is_thumbnail(key, prefix):
        new_img_name = prefix + key
        new_img_full_path = '/tmp/'+ new_img_name

        img_file = get_uploaded_image(bucket, key)

        image_to_thumbnail(img_file, new_img_full_path, size)

        response = upload_file(new_img_full_path, bucket, new_img_name)

        return response


def is_thumbnail(key, prefix):
    file_name = os.path.basename(key)
    return file_name.startswith(prefix)


def get_uploaded_image(bucket, key):
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=bucket, Key=key)
    file_stream = response['Body']
    image = Image.open(file_stream)
    return image


def image_to_thumbnail(img_file, new_img_full_path, size):
    img_file.thumbnail(size)
    img_file.save(new_img_full_path, "PNG")


def upload_file(file_name, bucket, object_name):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(Filename=file_name, Bucket=bucket, Key=object_name)
    except ClientError as e:
        logging.error(e)
        return False

    return True
