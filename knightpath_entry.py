import boto3
import json
import uuid

print('Loading function')
dynamodb = boto3.client('dynamodb')
lambda_client = boto3.client('lambda')
knightpath_moves_table_name = 'knightpath_moves'
    
def create_table_if_not_exists(table_name):
    """Creates the DynamoDB table if it doesn't exist."""
    tables = dynamodb.list_tables()['TableNames']
    if table_name not in tables:
        try:
            print(f"CREATING TABLE {table_name}")
            
            dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': 'operation_id', 'KeyType': 'HASH'}],  # Partition key
                AttributeDefinitions=[{'AttributeName': 'operation_id', 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
        except dynamodb.exceptions.ResourceInUseException:
            # Table already exists, so do nothing
            pass

def lambda_handler(event, context):
    create_table_if_not_exists(knightpath_moves_table_name)
   
    payload = event['body']
    source = payload.get('source')
    target = payload.get('target')

    # Input validation (basic check for chess squares)
    if not source or not target or len(source) != 2 or len(target) != 2:
        return {
            'statusCode': 400,
            'body': "Invalid input. Provide source and target as two-letter chess squares (e.g., A1, H8)."
        }

    # Create DynamoDB table if it doesn't exist
    create_table_if_not_exists(knightpath_moves_table_name)
    

    # # Generate operation ID and store request in DynamoDB
    operation_id = str(uuid.uuid4())
    
    resp = dynamodb.put_item(TableName=knightpath_moves_table_name,
        Item={
        'operation_id': {"S": operation_id},
        'source': {"S": source},
        'target': {"S": target}
    })
    
    
    lambda_client.invoke(
        FunctionName='arn:aws:lambda:us-west-1:471112639354:function:dowork',
        InvocationType='Event',
        Payload=json.dumps({"operation_id": operation_id}) 
    )
    
    return {
        'statusCode': 201,
        'body': f"Operation Id {operation_id} was created. Please query it to find your results."
    }
    
    
    
