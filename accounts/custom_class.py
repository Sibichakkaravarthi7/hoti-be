import uuid

from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import os

class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION

# Custom storage class for user uploaded files.
class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
