import boto3

dynamodb = boto3.resource("dynamodb")
connections = dynamodb.Table(os.environ["WebSocketConnection"])


def connect_handler(event, context):
    connection_id = event.get("requestContext", {}).get("connectionId")
    result = connections.put_item(Item={"connectionId": connection_id})
    return {"statusCode": 200, "body": "ok"}


def disconnect_handler(event, context):
    connection_id = event.get("requestContext", {}).get("connectionId")
    result = connections.delete_item(Key={"connectionId": connection_id})
    return {"statusCode": 200, "body": "ok"}

def message_handler(event, context):
    post_data = json.loads(event.get("body", "{}")).get("data")
    # print(post_data)
    domain_name = event.get("requestContext", {}).get("domainName")
    stage = event.get("requestContext", {}).get("stage")

    items = connections.scan(ProjectionExpression="connectionId").get("Items")
    if items is None:
        return {"statusCode": 500, "body": "something went wrong"}

    apigw_management = boto3.client(
        "apigatewaymanagementapi", endpoint_url=f"https://{domain_name}/{stage}"
    )
    for item in items:
        try:
            print(item)
            _ = apigw_management.post_to_connection(
                ConnectionId=item["connectionId"], Data=post_data
            )
        except:
            pass
    return {"statusCode": 200, "body": "ok"}
