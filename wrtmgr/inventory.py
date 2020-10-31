from configparser import ConfigParser


def iter_machines():
    inventory = ConfigParser()
    inventory.read('cfg/inventory.ini')

    secrets = ConfigParser()
    secrets.read('cfg/secrets.ini')

    # merge secrets into inventory config
    for section in secrets.sections():
        inventory[section].update(secrets[section])
    inventory['DEFAULT'].update(secrets['DEFAULT'])

    # iterate over machines
    for section in inventory.sections():
        variables = dict(inventory['DEFAULT'])
        variables.update(inventory[section])
        yield (section, variables)
