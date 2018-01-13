import requests
from threading import Thread
import time
import logging
import secrets

FORMAT = "[%(asctime)s %(name)s] %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SmartHomeDevice(object):
    def __init__(self, alexa_actions, alexa_id, alexa_name, alexa_description,
                 alexa_reachable, device_manufacturer, device_model, script_version,
                 additional_details=None):
        self.alexa_actions = alexa_actions
        self.alexa_id = alexa_id
        self.alexa_name = alexa_name
        self.alexa_description = alexa_description
        self.alexa_reachable = alexa_reachable
        self.device_manufacturer = device_manufacturer
        self.device_model = device_model
        self.script_version = script_version
        if not additional_details:
            self.additional_details = {}
        else:
            self.additional_details = additional_details

    def jsonify_device(self):
        json_blob = {
            "actions": self.alexa_actions,
            "additionalApplianceDetails": self.additional_details,
            "applianceId": self.alexa_id,
            "friendlyDescription": self.alexa_description,
            "friendlyName": self.alexa_name,
            "isReachable": self.alexa_reachable,
            "manufacturerName": self.device_manufacturer,
            "modelName": self.device_model,
            "version": self.script_version
        }

        return json_blob


class HookHomeDevice(SmartHomeDevice):
    def __init__(self, api_token, hook_id, alexa_id, alexa_name, alexa_description):
        alexa_actions = ['turnOn', 'turnOff']
        alexa_reachable = True
        device_manufacturer = 'EtekCity'
        device_model = 'RF Outlet'
        script_version = '1.0'

        self.api_address = 'https://api.gethook.io/v1/device/trigger'
        self.api_actions = ['On', 'Off']
        self.action_map = {'turnOn': 'On', 'turnOff': 'Off'}
        self.api_results = {'success': 0, 'failure': 0}
        self.hook_id = hook_id
        self.api_token = api_token
        super(self.__class__, self).__init__(
            alexa_actions, alexa_id, alexa_name, alexa_description,
            alexa_reachable, device_manufacturer, device_model, script_version)

    def get_api_url(self, action):
        return "{base_address}/{device_id}/{action}/?token={token}".format(
            base_address=self.api_address, device_id=self.hook_id,
            action=action, token=self.api_token
        )

    def add_result(self, result):
        if result == '1':
            self.api_results['success'] += 1
        else:
            self.api_results['failure'] += 1

    def execute_action(self, action, try_number=None):
        result = requests.get(self.get_api_url(action))
        trigger = result.json()['return_value']
        self.add_result(trigger)
        logger.info('Api Action: {}, Try: {}, Response: {}'.format(
            action, try_number, trigger))

    def thread_action(self, alexa_action, tries=10):
        self.api_results = {'success': 0, 'failure': 0}
        action = self.validate_alexa_action(alexa_action)
        threads = [Thread(target=self.execute_action, args=(action, try_number))
                   for try_number in range(1, tries + 1)]
        [t.start() for t in threads]
        # [t.join() for t in threads]

    def wait_for_response(self, timeout=10):
        sleep_increment = 0.05
        count = 0
        while self.api_results['success'] == 0 and count < (timeout / sleep_increment):
            time.sleep(0.05)
            count += 1

        logger.debug(self.api_results)
        if self.api_results['success'] > 0:
            return True
        else:
            return False

    def validate_alexa_action(self, alexa_action):
        if alexa_action not in self.alexa_actions:
            raise NotImplementedError

        else:
            return self.action_map[alexa_action]

    def create_payload(alexa_action):
        return {}


devices = {
    secrets.bedroom_1['hook_id']: HookHomeDevice(secrets.token, **secrets.bedroom_1),
    secrets.bedroom_2['hook_id']: HookHomeDevice(secrets.token, **secrets.bedroom_2),
    secrets.bedroom_3['hook_id']: HookHomeDevice(secrets.token, **secrets.bedroom_3),
    secrets.bedroom_4['hook_id']: HookHomeDevice(secrets.token, **secrets.bedroom_4),
    secrets.bedroom_5['hook_id']: HookHomeDevice(secrets.token, **secrets.bedroom_5)
}
