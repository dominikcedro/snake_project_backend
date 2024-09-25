"""
original author: Dominik Cedro
created: 2024-08-12
license: BSD 3.0
description: setup for cloud service Cloudinary and utility functions.
"""

import os
import cloudinary
import cloudinary.uploader
from cloudinary.uploader import upload
from fastapi import HTTPException, status, UploadFile
from dotenv import load_dotenv

load_dotenv()

cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
api_key = os.getenv('CLOUDINARY_API_KEY')
api_secret = os.getenv('CLOUDINARY_API_SECRET')
secure = os.getenv('CLOUDINARY_SECURE', 'True').lower() in ('true', '1', 't')

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
    secure=secure
)

async def upload_image(image: UploadFile):
    try:
        upload_result = upload(image.file)
        file_url = upload_result['secure_url']
        return file_url
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading images: {e}")