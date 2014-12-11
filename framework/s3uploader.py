"""
    :copyright: (c) 2011 Local Projects, all rights reserved
    :license: Affero GNU GPL v3, see LICENSE for more details.
"""

# !/usr/bin/env python

import mimetypes
import os.path
import sys

sys.path.append(os.path.dirname(__file__) + "/../")
from framework.config import *
from framework.log import log
from boto.s3.connection import S3Connection

class S3Uploader():
    @classmethod
    def upload(cls, source, destination):
        aws_config = Config.get('aws')
        conn = S3Connection(aws_config['access_key_id'], aws_config['secret_access_key'])
        print source
        if source == '.' or not os.path.isfile(source):
            log.error("file not found (%s)" % source)
            return False
        filehandle = open(source, 'rb')
        content_type = mimetypes.guess_type(source)[0]
        if not content_type:
            content_type = 'text/plain'
        log.info("Uploading %s to %s/%s" % (source, aws_config['bucket'], destination))
        bucket = conn.get_bucket(aws_config['bucket'])
        k = bucket.new_key(destination)
        k.set_metadata('Content-Type', content_type)
        number_of_bytes_written = k.set_contents_from_file(filehandle, policy='public-read')
        k.set_acl('public-read')
        if number_of_bytes_written == 0:
            log.error("--> Could not upload to S3!")
        return number_of_bytes_written


if __name__ == "__main__":
    try:
        source = sys.argv[1]
        destination = sys.argv[2]
    except IndexError, e:
        print "[SOURCE] [DESTINATION]"
    else:
        print S3Uploader.upload(source, destination)