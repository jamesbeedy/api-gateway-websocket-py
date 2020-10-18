#!/usr/bin/python3
"""Handle 'connect' and 'disconnect' operations."""
import json
import logging
import os

from datetime import datetime

import boto3


logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _get_response(status_code, body):
    """Ensure the body is json and return a formatted response."""
    if not isinstance(body, str):
        body = json.dumps(body)

    return {
        "statusCode": status_code,
        "body": body
    }


def handler(event, context):
    """Handle websocket default route connections."""
    connection_id = event["requestContext"]["connectionId"]
    event_type = event["requestContext"]["eventType"]

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['CONNECTIONS_TABLE'])

    if event_type == "CONNECT":
        logger.info("Connect requested")
        table.put_item(
            Item={
                'connectionId': connection_id,
                'ttl': int(datetime.utcnow().timestamp()),
            }
        )
        return _get_response(200, "Connect successful.")

    elif event_type == "DISCONNECT":
        logger.info("Disconnect requested")
        table.delete_item(
            Key={'connectionId': connection_id}
        )
        return _get_response(200, "Disconnect successful.")

    else:
        msg = (
            "Connection manager received "
            f"unrecognized eventType: '{event_type}'."
        )
        logger.error(msg)
        return _get_response(500, msg)
