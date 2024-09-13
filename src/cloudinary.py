import json
import os

import cloudinary
import cloudinary.uploader
from cloudinary.uploader import upload
from fastapi import HTTPException, status, UploadFile

# Configuration

dir_path = os.path.dirname(os.path.realpath(__file__))

config_path = os.path.join(dir_path, 'cloudinary_config.json')

with open(config_path) as f:
    config = json.load(f)
    cloud_name = config['cloud_name']
    api_key = config['api_key']
    api_secret = config['api_secret']
    secure = config['secure']

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=secure
    )

# Upload an image

async def upload_image(image: UploadFile):
    try:
        upload_result = upload(image.file)
        file_url = upload_result['secure_url']
        return file_url
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading images: {e}")