import os, boto3, traceback
from botocore.exceptions import NoCredentialsError
from credentials import INPUT_BUCKET, OUTPUT_BUCKET

class S3wrapper:
    obj = None
    def __init__(self):
        """Create a static connection to s3.
        
        :return: (bool) True if created or False if failed.
        """
        try:
            S3wrapper.obj = boto3.resource('s3', region_name='us-east-1')                
        except NoCredentialsError:
            print('Credentials not available!')
            return False
        except Exception:
            return False

    def upload_file(self, bucket_name, file_path, key_name):
        """Upload a file to an input s3 bucket.
        
        :param bucket_name: (str) Name of the bucket to upload into.
        :param file_path: (str) Path to the image file.
        :param key_name: (str) Name of the image file.
        :return: (bool) True if uploaded else False.
        """
        try:
            S3wrapper.obj.Bucket(bucket_name).upload_file(file_path, key_name)
            print('Upload Successful')
            return True
        except FileNotFoundError:
            print('The file was not found')
            return False
        except Exception:
            return False

    def upload_result(self, bucket_name, key, value):
        """Upload the classification result to an output s3 bucket.
        
        :param bucket_name: (str) Name of the bucket to upload into.
        :param key: (str) Name of the image file to be uploaded.
        :param value: (str) Classification result of the image file.
        :return: (bool) True if uploaded else False.
        """
        try:
            S3wrapper.obj.Object(bucket_name, key).put(Body=value)
            print('Upload Successful')
            return True
        except Exception:
            traceback.print_exc()
            print("Can't upload data!")
            return False

    def retrieve_value(self, bucket_name, key):
        """Retrieve contents of a bucket.
        
        :param bucket_name: (str) Name of bucket to retrieve from.
        :param key: (str) Name of the image file to retrieve.
        :return: (str) Value stored in the bucket having key `key`.
        """
        obj = S3wrapper.obj.Object(bucket_name, key)
        return obj.get()['Body'].read().decode('utf-8') 

class ObjectStore:
    s3 = S3wrapper()

    def __init__(self):
        pass

    @staticmethod
    def upload_input_images(location):
        """Upload the input image to s3 input bucket.

        :param location: (str) Location to the file on the local file-system.
        :return: (bool) True if uploaded else False.
        """
        key = location.split('/')[-1]
        return ObjectStore.s3.upload_file(INPUT_BUCKET, location, key)

    @staticmethod
    def upload_output_results(file_name, result):
        """Upload the output of the face recognition model to s3 output bucket.

        :param file_name: (str) File name of the input image.
        :param result: (str) Resulting classification from the DL model.
        :return: (bool) True if uploaded else False.
        """
        key = file_name.split('.')[0]
        return ObjectStore.s3.upload_result(OUTPUT_BUCKET, key, result)
