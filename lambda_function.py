""" Lambda function module """
import os
import logging
import boto3
from typing import Any, Dict
from aws_lambda_powertools.utilities.typing import LambdaContext

LOGGER = logging.getLogger()
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_IDP = boto3.client('cognito-idp')

def lambda_handler(event: Dict[str, Any], _context: LambdaContext) -> Dict[str, Any]:
    """ Handles function event and context """

    LOGGER.setLevel(logging.INFO)
    LOGGER.info('incoming event: %s', event)

    field = event.get('info', {}).get('fieldName')
    args = event.get('arguments', {})

    if field == 'getUserBasicInfo':
        # resolve backend api key from the secrets manager
        get_user_response = COGNITO_IDP.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=args.get('username')
        )
        username = get_user_response.get('Username')
        ua_list = get_user_response.get('UserAttributes')
        LOGGER.debug('result: %s', ua_list)

        return {
            'username': username,
            'picture': next((ua.get('Value') for ua in ua_list if ua.get('Name') == 'picture'), None),
            'bio': next((ua.get('Value') for ua in ua_list if ua.get('Name') == 'bio'), None),
            'contactable': next((ua.get('Value') for ua in ua_list if ua.get('Name') == 'contactable'), False)
        }

    raise ValueError('Unrecognized operation "{}"'.format(field))
