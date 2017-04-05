from home_skill_devices import devices


def parser(context, event):
    '''
    Entry for Discovery request
    '''

    response = {
        "discoveredAppliances": [device.jsonify_device() for device in devices.values()]
    }
    return True, response
