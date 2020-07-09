import botocore
import botocore.session
from botocore.config import Config
from scrapy.conf import settings
from scrapy.extensions import feedexport


class MinioUploader(feedexport.S3FeedStorage):
    def __init__(self, uri, access_key=None, secret_key=None):
        super(MinioUploader, self).__init__(uri)
        access_key = settings['AWS_ACCESS_KEY_ID']
        secret = settings['AWS_SECRET_ACCESS_KEY']
        endpoint = settings['AWS_ENDPOINT_URL']
        self.is_botocore = True
        self.s3_client = botocore.session.get_session().create_client(
            's3',
            endpoint_url=endpoint,
            use_ssl=False,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
