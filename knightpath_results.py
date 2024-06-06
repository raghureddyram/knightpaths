import boto3
import json

print('Loading function')
dynamodb = boto3.client('dynamodb')
table_name = 'knightpath_moves'



def lambda_handler(event, context):
    operation_id = event["queryStringParameters"].get('operationId')
    item = dynamodb.get_item(TableName=table_name, Key={
        'operation_id': {"S": operation_id}
    }).get("Item")
    
    if item:
        moves = item["num_moves"].get("N")
        shortest_path = item["shortest_path"].get("S")
        starting = item["source"].get("S")
        ending = item["target"].get("S")
        resp = {
            "starting": starting,
            "ending": ending,
            "shortestPath": shortest_path,
            "numberOfMoves": moves,
            "operationId": operation_id
        }
        
        return {"statusCode": 200, "body": json.dumps(resp)}
    
    return {"statusCode": 404, "body": "operation not found"}
        