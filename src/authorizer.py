#!/usr/bin/python3
"""Websocket authorizer module."""


def _authorizer_response(resource, effect):
    return {
        'principalId': 'me',
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }


def handler(event, context):
    """Authorize websocket connections."""
    headers = event['headers']
    method_arn = event['methodArn']

    if headers['X-Forwarded-Proto'] != 'https':
        return _authorizer_response(method_arn, "Deny")
    return _authorizer_response(method_arn, "Allow")
