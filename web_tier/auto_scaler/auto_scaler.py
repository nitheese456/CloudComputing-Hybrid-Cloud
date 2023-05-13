import boto3
import math
import time
import ec2_manager
from credentials import REQUEST_QUEUE_URL

# SQS Client.
client = boto3.client('sqs', region_name='us-west-2')

def scale_out():
    """
    Auto scale the ec2 instances depending on the length of the SQS queue. Based on the below criteria instances are scaled out:
    5 messages = 1 instance
    50 messages = 10 instances
    50+ messages = 19 instances
    """
    queue_len = int(client.get_queue_attributes(
        QueueUrl=REQUEST_QUEUE_URL,
        AttributeNames=['ApproximateNumberOfMessages']
        ).get('Attributes').get('ApproximateNumberOfMessages'))
    stopped_instances = ec2_manager.get_stopped_instances()
    running_instances = ec2_manager.get_running_instances()
    # running_instances.remove(WEB_INSTANCE_ID)
    num_of_instances_stopped = len(stopped_instances)
    num_of_instances_running = len(running_instances)

    if queue_len == 0:
        pass

    elif 1 <= queue_len <= 50  :
        needed_instances = math.ceil(queue_len / 5)
        if len(running_instances) < needed_instances:
            needed_instances -= num_of_instances_running
            if num_of_instances_stopped >= needed_instances:
                ec2_manager.bulk_start_instances(stopped_instances[:needed_instances])
            else:
                ec2_manager.bulk_start_instances(stopped_instances)
                for _ in range(needed_instances - num_of_instances_stopped):
                    ec2_manager.create_instance()

    else:
        if len(running_instances) < 19:
            needed_instances = 19 - num_of_instances_running
            if num_of_instances_stopped >= needed_instances:
                ec2_manager.bulk_start_instances(stopped_instances[:needed_instances])
            else:
                ec2_manager.bulk_start_instances(stopped_instances)
                for _ in range(needed_instances - num_of_instances_stopped):
                    ec2_manager.create_instance()

if __name__ == '__main__':
    while True:
        scale_out()
        time.sleep(5)
