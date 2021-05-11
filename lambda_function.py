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
        ua_obj = {x['Name']:x['Value'] for x in ua_list}
        # LOGGER.info('result: %s', ua_obj)

        return {
            'username': username,
            'picture': ua_obj.get('picture', None),
            'bio': ua_obj.get('bio', None),
            'contactable': ua_obj.get('custom:contactable', '').lower() == 'true',
            'identityId': ua_obj.get('custom:identityId', None)
        }

    raise ValueError('Unrecognized operation "{}"'.format(field))
