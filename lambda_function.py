""" Lambda function module """
import os
import logging
import boto3

LOGGER = logging.getLogger()
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_IDP = boto3.client('cognito-idp')

def lambda_handler(event, _context):
    """ Handles function event and context """
    # Set log level
    LOGGER.setLevel(logging.INFO)

    # Expected Event
    # {
    #   "field": "getUser",
    #   "arguments": {
    #     "username": "postId1"
    #   }
    # }

    payload = event['payload']
    field = payload.get('field')
    args = payload.get('arguments')

    if field == 'getUser':

        # resolve backend api key from the secrets manager
        get_user_response = COGNITO_IDP.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=args.get('username')
        )

        username = get_user_response.get('Username')
        ua_list = get_user_response.get('UserAttributes')
        LOGGER.debug('result: %s ', ua_list)

        return {
            'username': username,
            'picture': next((ua.get('Value') for ua in ua_list if ua.get('Name') == 'picture'), ''),
            'bio': next((ua.get('Value') for ua in ua_list if ua.get('Name') == 'bio'), ''),
            'contactable': next((ua.get('Value') for ua in ua_list if ua.get('Name') == 'contactable'), False)
        }

    raise ValueError('Unrecognized operation "{}"'.format(field))
