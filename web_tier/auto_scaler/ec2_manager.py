import boto3
from credentials import AMI_ID, KEY_NAME, SECURITY_GROUP, ROLE_ARN

# Create Ec2 Client
ec2_client = boto3.client('ec2', region_name='us-east-1')

def create_instance():
    """Create an ec2 instance from custom AMI."""
    instances = ec2_client.run_instances(
        ImageId=AMI_ID,
        InstanceType='t2.micro',
        KeyName=KEY_NAME,
        SecurityGroupIds=[SECURITY_GROUP],
        IamInstanceProfile={'Arn': ROLE_ARN},
        MinCount=1,
        MaxCount=1,
    )

def bulk_create_instances(num):
    """Bulk create `num` instances one after another.

    :param num: (int) Number of instances to be created.
    """
    for _ in range(num):
        create_instance()

def start_instance(instance_id):
    """Start an ec2 instance.
    
    :param instance_id: (str) ID of the instance to be created.
    """
    response = ec2_client.start_instances(InstanceIds=[instance_id], DryRun=False)
    print(response)

def bulk_start_instances(instance_ids):
    """Bulk start ec2 instances one after another.
    
    :param instance_ids: (list) List of strings of instance IDs.
    """
    for i in instance_ids:
        start_instance(i)

def stop_instance(instance_id):
    """Stop an ec2 instance.
    
    :param instance_id: (str) ID of the instance to stop.
    """
    ec2_client.stop_instances(InstanceIds=[instance_id])

def bulk_stop_instances(instance_ids):
    """Bulk stop ec2 instances one after another.
    
    :param instance_ids: (list) List of strings of instance IDs.
    """
    for i in instance_ids:
        stop_instance(i)

def get_running_instances():
    """Get number of running instances.

    :return: (list) List of strings of instance IDs which are in running state.
    """
    instance_list = list()
    reservations = ec2_client.describe_instances(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running', 'pending'],
    }]).get('Reservations')

    for reservation in reservations:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_list.append(instance_id)
    return instance_list

def get_stopped_instances():
    """Get number of stopped instances.
    
    :return: (list) List of strings of instance IDs which are in stopped state.
    """
    instance_list = list()
    reservations = ec2_client.describe_instances(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['stopped'],
    }]).get('Reservations')

    for reservation in reservations:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_list.append(instance_id)
    return instance_list

def get_all_instances():
    """Get all running and stopped instances.
    
    :return: (list) List of strings of instance IDs which are running or stopped.
    """
    instance_list = list()
    reservations = ec2_client.describe_instances(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running', 'stopped'],
    }]).get('Reservations')

    for reservation in reservations:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_list.append(instance_id)
    return instance_list
