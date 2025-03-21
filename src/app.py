from datetime import datetime, timezone
import json
import uuid
import boto3
import os

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

table_name = os.environ['TABLE_NAME']
queue_url = os.environ['QUEUE_URL']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        # Handle preflight OPTIONS request for CORS
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': 'http://form.wootangly.com',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': ''
            }
        
        # Handle POST request
        if event['httpMethod'] == 'POST':
            # Parse incoming transaction data
            body = json.loads(event['body'])
            transaction_id = str(uuid.uuid4())

            # Use datetime.now(timezone.utc) for UTC timestamp
            transaction_data = {
                'transactionId': transaction_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': body
            }

            # Store transaction data in DynamoDB
            table.put_item(Item=transaction_data)

            # Send transaction ID to SQS for further processing
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(transaction_data)
            )

            # Return successful response
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': 'http://form.wootangly.com',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'message': 'Transaction logged successfully',
                    'transactionId': transaction_id
                })
            }

        # Return method not allowed if unsupported HTTP method is used
        return {
            'statusCode': 405,
            'headers': {
                'Access-Control-Allow-Origin': 'http://form.wootangly.com',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'message': 'Method not allowed'})
        }

    except Exception as e:
        # Handle any errors
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': 'http://form.wootangly.com',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'message': 'Error logging transaction',
                'error': str(e)
            })
        }
