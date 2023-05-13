import boto3
from botocore.exceptions import NoCredentialsError

class SQSwrapper:
    obj = None
    def __init__(self):
        """Create a static connection to SQS.
        
        :return: (bool) True if created or False if failed.
        """
        try:
            SQSwrapper.obj = boto3.client('sqs', region_name='us-west-2')
        except NoCredentialsError:
            print('Credentials not available')
            return False
        except Exception:
            return False

    def create_queue(self, name):
        """Create a queue with given name.

        :param name: (str) Name of queue to be created.
        :return: (dict) Contains key `Queueurl` with values having actual url.
        """
        return SQSwrapper.obj.create_queue(QueueName=name, Attributes={'DelaySeconds': '5'})

    def get_queue_by_name(self, name):
        """Get a queue by the given name.
        
        :param name: (str) Name of queue to retrieve.
        :return: (sqs.Queue) Queue resource object of given name.
        """
        return SQSwrapper.obj.get_queue_by_name(QueueName=name)

    def send_message(self, queue_url, message):
        """Send a message into given queue.
        
        :param queue_url: (str) Url of the queue to send to.
        :param message: (str) The message body to send.
        """
        SQSwrapper.obj.send_message(QueueUrl=queue_url, MessageBody=message)

    def get_queue_attributes(self, queue_url, attributes):
        """Gets attributes for the specified queue.
        
        :param queue_url: (str) Url of the queue to get attributes of.
        :param attributes: (list) List of strings of attribute names.
        :return: (dict) Queue attributes with string values.
        """
        return SQSwrapper.obj.get_queue_attributes(QueueUrl=queue_url,AttributeNames=attributes)

    def get_latest_message(self, queue_url):
        """Gets the first available message in queue.
        
        :param queue_url: (str) Url of the queue to get message from.
        :return: (dict) Message attributes with string values.
        """
        response = SQSwrapper.obj.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            VisibilityTimeout=10,
            WaitTimeSeconds=0
        )
        return response

    def delete_message(self, queue_url, receipt_handle):
        """Delete a message from the specified queue.

        :param queue_url: (str) Url of the queue to delete from.
        :param receipt_handle: (str) ID of the message to be deleted.
        """
        SQSwrapper.obj.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

class Queue:
    sqs = SQSwrapper()

    def __init__(self):
        pass

    @staticmethod
    def get_num_messages_available(queue_url):
        """Get the number of messages in the queue.
        
        :param queue_url: (str) Url of the queue to get messages from.
        :return: (int) Number of available messages.
        """
        response = Queue.sqs.get_queue_attributes(queue_url, ['ApproximateNumberOfMessages'])
        messages_available = response['Attributes']['ApproximateNumberOfMessages']
        return int(messages_available)

    @staticmethod
    def get_num_message_not_visible(queue_url):
        """Get the number of messages not visible in the queue.
        
        :param queue_url: (str) Url of the queue to get messages from.
        :return: (int) Number of non-visible messages.
        """
        response = Queue.sqs.get_queue_attributes(queue_url, ['ApproximateNumberOfMessagesNotVisible'])
        messages_not_visible = response['Attributes']['ApproximateNumberOfMessagesNotVisible']
        return int(messages_not_visible)

    @staticmethod
    def get_latest_message(queue_url):
        """Get the first available message in queue.
        
        :param queue_url: (str) Url of the queue to get message from.
        :return: None or (str, str) Result and classification of the image.
        """
        response = Queue.sqs.get_latest_message(queue_url)
        if 'Messages' not in response:
            print('Queue is empty')
            return None
        receipt_handle = response['Messages'][0]['ReceiptHandle']
        print(type(receipt_handle))
        result = response['Messages'][0]['Body']
        return result, receipt_handle

    @staticmethod
    def delete_message(queue_url, receipt_handle):
        """Delete a message from the specified queue.
        
        :param queue_url: (str) Url of the queue.
        :param receipt_handle: (str) ID of the message.
        """
        Queue.sqs.delete_message(queue_url, receipt_handle)

    @staticmethod
    def send_message(queue_url, message):
        """Send a message to specified queue.
        
        :param queue_url: (str) Url of the queue.
        :param message: (str) Body of message to send.
        """
        Queue.sqs.send_message(queue_url, message)
