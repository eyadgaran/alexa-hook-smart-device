# Skill enters here and gets routed appropriately
import logging
import discovery
import control
import uuid
import requests
import secrets

FORMAT = "[%(asctime)s %(name)s] %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    """
    Entry function of API Call
    event and context get passed and parsed appropriately
    :param event:
    :param context:
    :return:
    :rtype:
    """
    logger.debug(event)
    logger.debug(context)

    access_token = event['payload']['accessToken']
    logger.info("Token: {}".format(access_token))
    validate_access_token(access_token)

    alexa_request = event['header']['name']
    namespace = event['header']['namespace']
    api_version = event['header']['payloadVersion']

    logger.info('Directive: {}'.format(namespace))
    logger.info('Request: {}'.format(alexa_request))

    if namespace == 'Alexa.ConnectedHome.Discovery':
        success, payload = discovery.parser(context, event)

    elif namespace == 'Alexa.ConnectedHome.Control':
        success, payload = control.parser(context, event)

    else:
        logger.info(event)
        raise NotImplementedError

    header = generate_header(success, alexa_request, namespace, api_version)

    return generate_response(header, payload)


def generate_header(success, alexa_request, namespace, payload_version):
    message_id = str(uuid.uuid1())
    logger.info("Action Succeeded: {}".format(success))

    if success:
        name = request_mapper(alexa_request)
    else:
        name = "DriverInternalError"

    header = {
        "messageId": message_id,
        "name": name,
        "namespace": namespace,
        "payloadVersion": payload_version
    }

    return header


def generate_response(header, payload):
    response = {
        "header": header,
        "payload": payload
    }

    logger.debug(response)

    return response


def request_mapper(alexa_request):
    '''
    Maps the corresponding return header to the incoming request
    '''
    request_map = {
        "DiscoverAppliancesRequest": "DiscoverAppliancesResponse",
        "TurnOnRequest": "TurnOnConfirmation",
        "TurnOffRequest": "TurnOffConfirmation",
        "GetLockStateRequest": "GetLockStateResponse",
        "SetLockStateRequest": "SetLockStateConfirmation",
        "GetTemperatureReadingRequest": "GetTemperatureReadingResponse",
        "GetTargetTemperatureRequest": "GetTargetTemperatureResponse",
        "SetTargetTemperatureRequest": "SetTargetTemperatureConfirmation",
        "IncrementTargetTemperatureRequest": "IncrementTargetTemperatureConfirmation",
        "DecrementTargetTemperatureRequest": "DecrementTargetTemperatureConfirmation",
        "SetPercentageRequest": "SetPercentageConfirmation",
        "IncrementPercentageRequest": "IncrementPercentageConfirmation",
        "DecrementPercentageRequest": "DecrementPercentageConfirmation",
        "HealthCheckRequest": "HealthCheckResponse"
    }

    return request_map[alexa_request]


def validate_access_token(token):
    base_url = 'https://api.amazon.com/user/profile?access_token='
    profile = requests.get(base_url + token)

    profile_id = profile.json()['user_id']

    personal_profile = secrets.personal_alexa_profile

    if profile_id != personal_profile:
        logger.debug(profile.json())
        raise ValueError("Invalid Token")

    logger.info("User: {} ({}), Authenticated".format(
        profile.json()['name'], profile_id))
