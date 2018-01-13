from home_skill_devices import devices


def parser(context, event):
    '''
    Entry for control operations
    '''
    device = devices[event['payload']['appliance']['applianceId']]
    name = event['header']['name']
    device.thread_action(action_map(name))

    success = device.wait_for_response()

    if success:
        return True, device.create_payload()

    else:
        return False, {}


def action_map(name):
    alexa_map = {
        "TurnOnRequest": "turnOn",
        "TurnOffRequest": "turnOff"
    }

    return alexa_map[name]
