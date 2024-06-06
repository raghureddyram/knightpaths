import json
import boto3
from collections import deque

dynamodb = boto3.client('dynamodb')
table_name = 'knightpath_moves'
start_finish_table_name='start_finish'


def calculate_knight_path(source, target):
    # Convert chess notation to (row, col) coordinates (0-indexed)
    def to_coords(square):
        col = ord(square[0]) - ord('A')
        row = 8 - int(square[1])
        return row, col

    source = to_coords(source)
    target = to_coords(target)

    
    moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

    # BFS Queue: (current_position, path_so_far_array)
    queue = deque([(source, [source])])

    # Keep track of visited squares
    visited = set([source])

    while queue:
        current, path = queue.popleft()
        if current == target:
            #Convert to desired format
            formatted_path = ":".join([f"{chr(col + ord('A'))}{8 - row}" for row, col in path])
            return formatted_path, len(path) - 1  # Number of moves

        for move in moves:
            next_row, next_col = current[0] + move[0], current[1] + move[1]
            if 0 <= next_row < 8 and 0 <= next_col < 8 and (next_row, next_col) not in visited:
                queue.append(((next_row, next_col), path + [(next_row, next_col)]))
                visited.add((next_row, next_col))

    return None, None

def create_cache_table_if_not_exists():
    """Creates the DynamoDB table if it doesn't exist."""
    tables = dynamodb.list_tables()['TableNames']
    if start_finish_table_name not in tables:
        try:
            print(f"CREATING TABLE {start_finish_table_name}")
            
            dynamodb.create_table(
                TableName=start_finish_table_name,
                KeySchema=[{'AttributeName': 'start_and_end', 'KeyType': 'HASH'}],  # Partition key
                AttributeDefinitions=[{'AttributeName': 'start_and_end', 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
        except dynamodb.exceptions.ResourceInUseException:
            # Table already exists, so do nothing
            pass

def lambda_handler(event, context):
    create_cache_table_if_not_exists()

    operation_id = event["operation_id"]
    item = dynamodb.get_item(TableName=table_name, Key={
        'operation_id': {"S": operation_id}
    })["Item"]
    
    source = item.get('source')
    target = item.get('target')
    if not source or not target:
        return {
            'statusCode': 422,
            'body': "Source and target required."
        }
    
    existing_short_path_item = dynamodb.get_item(TableName=start_finish_table_name, Key={
        'start_and_end': {"S": f"{source}->{target}"}
    }).get("Item")

    if existing_short_path_item:
        print("Found cached path")
        try:
            shortest_path = existing_short_path_item["shortest_path"].get("S")
            num_moves = existing_short_path_item["num_moves"].get("N")
            dynamodb.update_item(
                TableName=table_name,
                Key={'operation_id': {'S': operation_id}},
                UpdateExpression="SET shortest_path = :path, num_moves = :moves",
                ExpressionAttributeValues={
                    ':path': {'S': shortest_path},
                    ':moves': {'N': str(num_moves)}
                }
            )
        except Exception as e:
            print(f"ERROR {e}")
            return {
                'statusCode': 500,
                'body': f"Error storing results: {e}"
            }
        return {
            'statusCode': 200,
            'body': "Path calculation completed successfully."
        }
    
    shortest_path, num_moves = calculate_knight_path(source.get("S"), target.get("S"))
    if shortest_path is None:
        print("NO Path")
        return {
            'statusCode': 422,
            'body': "Path calculation not processed."
        }
    
    try:
        dynamodb.update_item(
            TableName=table_name,
            Key={'operation_id': {'S': operation_id}},
            UpdateExpression="SET shortest_path = :path, num_moves = :moves",
            ExpressionAttributeValues={
                ':path': {'S': shortest_path},
                ':moves': {'N': str(num_moves)}
            }
        )

        dynamodb.update_item(
            TableName=start_finish_table_name,
            Key={'start_and_end': {'S': f"{source}->{target}"}},
            UpdateExpression="SET shortest_path = :path, num_moves = :moves",
            ExpressionAttributeValues={
                ':path': {'S': shortest_path},
                ':moves': {'N': str(num_moves)}
            }
        )

    except Exception as e:
        print(f"ERROR {e}")
        return {
            'statusCode': 500,
            'body': f"Error storing results: {e}"
        }

    print("Successfully calculated and stored path")
    return {
        'statusCode': 200,
        'body': "Path calculation completed successfully."
    }
    