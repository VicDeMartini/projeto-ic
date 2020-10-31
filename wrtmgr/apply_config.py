from .inventory import iter_machines
from configparser import ConfigParser
from tempfile import NamedTemporaryFile
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


env = Environment(
    loader=FileSystemLoader('templates'),
)


def apply_configs(machine, templates, variables):
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(AutoAddPolicy())

    ssh.connect(machine, username='root')
    scp = SCPClient(ssh.get_transport())

    something_changed = False
    
    for template_name, template_dest in templates.items():
        template = env.get_template(template_name)
        new_contents = template.render(**variables).encode('utf-8')

        with NamedTemporaryFile() as tmp_file:
            scp.get(template_dest, tmp_file.name)
            old_contents = tmp_file.read()

        if old_contents != new_contents:
            something_changed = True
            scp.putfo(BytesIO(new_contents), template_dest)

    scp.close()

    if something_changed:
        ssh.exec_command('reload_config')

    print(machine, '[changed]' if something_changed else '[ok]')

    ssh.close()


def main(args):
    templates_config = ConfigParser()
    templates_config.read('cfg/templates.ini')
    templates = templates_config['DEFAULT']

    for machine, variables in iter_machines():
        apply_configs(machine, templates, variables)

