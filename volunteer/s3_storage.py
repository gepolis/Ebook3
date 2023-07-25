from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    bucket_name = '32199b4c-32199b4c'
    location = 'media'

