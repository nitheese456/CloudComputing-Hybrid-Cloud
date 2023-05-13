import os
import json
import uuid
import base64
import boto3

from flask import (Flask, request)

app = Flask(__name__)

sqs = boto3.client('sqs', region_name='us-west-2')
s3 = boto3.resource('s3', region_name='us-west-2')

request_queue_url = 'https://sqs.us-west-2.amazonaws.com/399414555557/Request-Queue'
response_queue_url = 'https://sqs.us-west-2.amazonaws.com/399414555557/Response-Queue'


@app.route('/upload-image', methods=['POST'])
def process():
    """
    Upload the images to the input SQS queue and show the classified results.

    :return: (str) The classification of the image.
    """
    print("hello")
    try:
        input_file = request.files.get('myfile')
        print("input_file",input_file)
        if input_file.filename:
            id = str(uuid.uuid4())
            converted_string = base64.b64encode(input_file.read())
            sqs_message_body = {
                'encoded_image': str(converted_string, 'utf-8'),
                'unique_id': id,
                'file_name': input_file.filename
            }
            # Send message to SQS queue.
            sqs.send_message(
                QueueUrl=request_queue_url,
                MessageBody=json.dumps(sqs_message_body)
            )
        print('Uploaded file to the request queue!')
        # Poll the response queue to get the classfication of the image.
        while True:
            sqs_output = sqs.receive_message(
                QueueUrl=response_queue_url,
                AttributeNames=['All'],
                MaxNumberOfMessages=10,
                WaitTimeSeconds=1
            )
            messages = sqs_output.get('Messages', [])
            for item in messages:
                msg_body = json.loads(item.get('Body'))
                if msg_body['unique_id'] == id: 
                    sqs.delete_message(
                        QueueUrl=response_queue_url,
                        ReceiptHandle=item.get('ReceiptHandle')
                    )
                    return msg_body.get('classification')
    except Exception as e:
        print(e)
        return ''

if __name__ == '__main__':
    app.run(
        host=os.getenv('LISTEN', '0.0.0.0'),
        port=int(os.getenv('PORT', '8080'))
    )
