import json
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def lambda_handler(event, context):
    optimization_report = event

    queue_url = os.environ.get('SQS_QUEUE_URL')
    if not queue_url:
        raise ValueError("SQS_QUEUE_URL not found in .env file.")
        
    print("Sending report to SQS....")

    try:
        sqs = boto3.client('sqs')
        message_body = json.dumps(optimization_report)
        
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body
        )
        
        message_id = response.get('MessageId')
        print(f"Report sent to SQS with MessageId: {message_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Report sent successfully!', 'messageId': message_id})
        }
    except Exception as e:
        print(f"Error sending report to SQS: {e}")
        raise e