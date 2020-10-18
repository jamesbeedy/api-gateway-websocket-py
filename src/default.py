#!/usr/bin/python3
"""Default websocket route."""
import json
import logging
import os
import sys

import boto3
from boto3.ApiGatewayManagementApi.Client.exceptions import (
    ForbiddenException,
    GoneException,
    LimitExceededException,
    PayloadTooLargeException,
)


logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _send_to_connection(connection_id, data, event):
    """Send data to websocket connection via connection_id."""
    json_data = ""
    stage = event["requestContext"]["stage"]
    domain_name = event["requestContext"]["domainName"]

    try:
        json_data = json.dumps(data)
    except json.JSONDecodeError as e:
        logger.error(e)
        return False

    try:
        apigw = boto3.client(
            'apigatewaymanagementapi',
            f"https://{domain_name}/{stage}"
        )
        apigw.post_to_connection(
            ConnectionId=connection_id,
            Data=json_data.encode('utf-8'),
        )
    except (GoneException,
            LimitExceededException,
            PayloadTooLargeException,
            ForbiddenException) as e:
        logger.error(e)
        return False

    return True


def _get_all_connections():
    """Return all connections by connectionId."""
    dynamodb = boto3.client('dynamodb')
    table_name = os.environ['CONNECTIONS_TABLE']

    connection_ids = dynamodb.scan(
        TableName=table_name,
        ProjectionExpression='connectionId',
    )
    return [
        item['connectionId']['S']
        for item in connection_ids['Items'] if 'connectionId' in item
    ]


def default(event, context):
    """Websocket handler."""
    body = json.loads(event['body'])

    current_connection_id = event['requestContext']['connectionId']
    connection_ids = _get_all_connections()

    for connection_id in connection_ids:
        if connection_id != current_connection_id:
            if not _send_to_connection(connection_id, body, event):
                logger.debug(f"Cannot send to connection: {connection_id}.")
                sys.exit(1)

    return {'statusCode': 200}
