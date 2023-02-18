import boto3
import time

def createS3Bucket(s3Resource, bucketName):
    s3Resource.create_bucket(Bucket=bucketName)

def uploadFileToBucket(s3Client, bucketName, fileName):
    s3Client.upload_file(fileName, bucketName, fileName)

def downloadFileFromBucket(s3Client, bucketName, fileName):
    s3Client.download_file(bucketName, fileName, fileName)

def createSnsTopic(snsClient, topicName):
    response = snsClient.create_topic(Name=topicName)
    snsTopicArn = response['TopicArn']
    return snsTopicArn

def SubscribeToTopic(snsClient, snsTopicArn):
    response = snsClient.subscribe(
    TopicArn=snsTopicArn,
    Protocol='email',
    Endpoint='dinachoshha@gmail.com',
    ReturnSubscriptionArn=True|False)


def addPolicyToPublishMessages(snsClient, snsTopicArn):
    policyValue = """{
    "Version": "2012-10-17",
    "Id": "example-ID",
    "Statement": [
        {
        "Sid": "example-statement-ID",
        "Effect": "Allow",
        "Principal": {
            "AWS": "*"
        },
        "Action": "SNS:Publish",
        "Resource": "arn:aws:sns:us-east-1:166145399123:s3UploadTopic",
        "Condition": {
            "StringEquals": {
            "aws:SourceAccount": "166145399123"
            },
            "ArnLike": {
            "aws:SourceArn": "arn:aws:s3:::test-bucket-15022023"
            }
        }
        }
    ]
    }"""


    response = snsClient.set_topic_attributes(
    TopicArn=snsTopicArn,
    AttributeName='Policy',
    AttributeValue=policyValue)

def addEventNotificationToBucket(s3Client, snsTopicArn, bucketName):
    response = s3Client.put_bucket_notification_configuration(
    Bucket=bucketName,
    NotificationConfiguration={
        'TopicConfigurations': [
            {
                'TopicArn': snsTopicArn,
                'Events': ['s3:ObjectCreated:Put']
            },
        ],
    },
    )

def createIamUsers(s3Client, userName):
    response = s3Client.create_user(
    UserName=userName)

def createAcessKeyForUser(s3Client, userName):
    response = s3Client.create_access_key(
    UserName=userName
    )
    return response

def createUploadToS3Policy(iamClient):
    response = iamClient.create_policy(
    PolicyName='uploadToS3Policy',
    PolicyDocument="""{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::test-bucket-15022023/*"
        }
    ]
    }"""
    )
    return response['Policy']['Arn']

def createDownloadFromS3Policy(iamClient):
    response = iamClient.create_policy(
    PolicyName='downloadFromS3Policy',
    PolicyDocument="""{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::test-bucket-15022023/*"
        }
    ]
    }"""
    )
    return response['Policy']['Arn']

def attachPolicyToUser(iamClient, userName, PolicyArn):
    response = iamClient.attach_user_policy(
    UserName=userName,
    PolicyArn=PolicyArn
)

def uploadFileWithProfile(profileDetailsDict, bucketName, fileName):
    client = boto3.client(
    's3',
    aws_access_key_id=profileDetailsDict['AccessKey']['AccessKeyId'],
    aws_secret_access_key=profileDetailsDict['AccessKey']['SecretAccessKey']
    )

    uploadFileToBucket(client, bucketName, fileName)

def downloadFileWithProfile(profileDetailsDict, bucketName, fileName):
    client = boto3.client(
    's3',
    aws_access_key_id=profileDetailsDict['AccessKey']['AccessKeyId'],
    aws_secret_access_key=profileDetailsDict['AccessKey']['SecretAccessKey']
    )

    downloadFileFromBucket(client, bucketName, fileName)

def main():
    s3Resource = boto3.resource('s3')
    s3Client = boto3.client('s3')
    bucketName = 'test-bucket-15022023'
    
    # 1.
    createS3Bucket(s3Resource, bucketName)
    fileName = 'hello.txt'
    uploadFileToBucket(s3Client, bucketName, fileName)
    downloadFileFromBucket(s3Client, bucketName, fileName)

    # 2.
    snsClient = boto3.client('sns')
    topicName = 's3UploadTopic'
    snsTopicArn = createSnsTopic(snsClient, topicName)
    SubscribeToTopic(snsClient, snsTopicArn)
    addPolicyToPublishMessages(snsClient, snsTopicArn)
    addEventNotificationToBucket(s3Client, snsTopicArn, bucketName)

    # 3.
    iamClient = boto3.client('iam')
    publisherName = 'publisher'
    receiverName = 'receiver'
    createIamUsers(iamClient, publisherName)
    createIamUsers(iamClient, receiverName)

    publisherDetailsDict = createAcessKeyForUser(iamClient, publisherName)
    receiverDetailsDict = createAcessKeyForUser(iamClient, receiverName)

    uploadPilcyArn = createUploadToS3Policy(iamClient)
    downloadPolicyArn = createDownloadFromS3Policy(iamClient)

    attachPolicyToUser(iamClient, publisherName, uploadPilcyArn)
    attachPolicyToUser(iamClient, receiverName, downloadPolicyArn)

    uploadFileWithProfile(publisherDetailsDict, bucketName, 'test.txt')
    downloadFileWithProfile(publisherDetailsDict, bucketName, 'test.txt')
    downloadFileWithProfile(receiverDetailsDict, bucketName, 'test.txt')
    uploadFileWithProfile(receiverDetailsDict, bucketName, 'test.txt')

main()