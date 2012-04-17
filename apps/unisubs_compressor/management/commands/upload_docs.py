"""
Upload Doc
==========

Django command that scans all files in from the sphinx doc build to s3


"""
import mimetypes
import optparse
import os
import re

from django.core.management.base import BaseCommand, CommandError

# Make sure boto is available
try:
    import boto
    import boto.exception
except ImportError:
    raise ImportError, "The boto Python library is not installed."

class Command(BaseCommand):

    # Extra variables to avoid passing these around
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    AWS_BUCKET_NAME = ''
    DIRECTORY = ''
    FILTER_LIST = [re.compile(x) for x in ['\.DS_Store', '_sources*.*', ".doctrees*.*"]]

    upload_count = 0
    skip_count = 0
    PREFIX = 'docs/'
    help = 'Syncs the complete STATIC_ROOT/docs structure and files to S3 into the given bucket name.'

    can_import_settings = True

    def handle(self, *args, **options):
        from django.conf import settings

        if not hasattr(settings, 'STATIC_ROOT'):
            raise CommandError('STATIC_ROOT must be set in your settings.')
        else:
            if not settings.STATIC_ROOT:
                raise CommandError('STATIC_ROOT must be set in your settings.')
        self.DIRECTORY = os.path.join(settings.STATIC_ROOT, 'docs')
        # Check for AWS keys in settings
        if not hasattr(settings, 'AWS_ACCESS_KEY_ID') or \
           not hasattr(settings, 'AWS_SECRET_ACCESS_KEY'):
           raise CommandError('Missing AWS keys from settings file.  Please' +
                     'supply both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.')
        else:
            self.AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
            self.AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY

        if not hasattr(settings, 'AWS_BUCKET_NAME'):
            raise CommandError('Missing bucket name from settings file. Please' +
                ' add the AWS_BUCKET_NAME to your settings file.')
        else:
            if not settings.AWS_BUCKET_NAME:
                raise CommandError('AWS_BUCKET_NAME cannot be empty.')
        self.AWS_BUCKET_NAME = settings.AWS_BUCKET_NAME 
        self.verbosity = int(options.get('verbosity'))
        self.sync_s3()


    def sync_s3(self):
        """
        Walks the media directory and syncs files to S3
        """
        bucket, key = self.open_s3()
        os.path.walk(self.DIRECTORY, self.upload_s3,
            (bucket, key, self.AWS_BUCKET_NAME, self.DIRECTORY))

    def open_s3(self):
        """
        Opens connection to S3 returning bucket and key
        """
        conn = boto.connect_s3(self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY)
        try:
            bucket = conn.get_bucket(self.AWS_BUCKET_NAME)
        except boto.exception.S3ResponseError:
            bucket = conn.create_bucket(self.AWS_BUCKET_NAME)
        return bucket, boto.s3.key.Key(bucket)

    def upload_s3(self, arg, dirname, names):
        """
        This is the callback to os.path.walk and where much of the work happens
        """
        bucket, key, bucket_name, root_dir = arg # expand arg tuple

        if not root_dir.endswith('/'):
            root_dir = root_dir + '/'

        for file in names:
            filename = os.path.join(dirname, file)
            for p in self.FILTER_LIST:
                if p.match(file) or p.match(filename):
                    print "not uplodaing! filtering ", file
                    continue # Skip files we don't want to sync
            if os.path.isdir(filename):
                continue # Don't try to upload directories
            file_key = filename[len(root_dir):]
            self.upload_one(bucket, key, bucket_name, root_dir, filename, file_key)                    


    def upload_one(self, bucket, key, bucket_name, root_dir, filename, 
                   file_key):
        if self.verbosity > 0:
            print "Uploading %s..." % (file_key)
        headers = {}
        content_type = mimetypes.guess_type(filename)[0]
        if content_type:
            headers['Content-Type'] = content_type
        file_obj = open(filename, 'rb')
        filedata = file_obj.read()
        try:
            key.name = self.PREFIX +file_key
            key.set_contents_from_string(filedata, headers, replace=True)
            key.make_public()
        except boto.s3.connection.BotoClientError, e:
            print "Failed: %s" % e
        except Exception, e:
            print e
            raise
        else:
            self.upload_count += 1

        file_obj.close()

# Backwards compatibility for Django r9110
if not [opt for opt in Command.option_list if opt.dest=='verbosity']:
    Command.option_list += (
        optparse.make_option('-v', '--verbosity',
            dest='verbosity', default=1, action='count',
            help="Verbose mode. Multiple -v options increase the verbosity."),
    )
