import os

import yaml

CONFIG_FILE = os.path.expanduser('~/.cli/config')
LOCAL_ENV_FILE = os.path.expanduser('~/.cli/%s.env' % os.getcwd().replace('/', '-'))

if not os.path.exists(os.path.expanduser('~/.cli')):
    os.mkdir(os.path.expanduser('~/.cli'))


def load_environment_variables(file_name):
    # Load local environment variables
    if os.path.exists(file_name):
        with open(file_name, 'r', newline='') as file:
            for line in file.readlines():
                name, value = line.split('=')
                os.environ[name] = value.strip()


def set_environment_variables(
        local_variable,
        local_variable_value=None,
        file_name=LOCAL_ENV_FILE,
        verbose=True,
        exit_on_complete=True):
    file_name = os.path.expanduser(file_name)
    if local_variable:
        if local_variable_value is None:
            if '=' not in local_variable or local_variable.endswith('='):
                raise SyntaxError('--set-local-variable must be in the format NAME=VALUE')
            local_variable, local_variable_value = local_variable.split('=')

        local_variable_value = str(local_variable_value)
        if os.path.exists(file_name):
            with open(file_name, 'r', newline='') as file:
                file_lines = file.readlines()
        else:
            file_lines = []

        for line in file_lines:
            if line.startswith(local_variable + '='):
                file_lines.remove(line)
                break

        file_lines.append(local_variable + '=' + local_variable_value + '\n')

        with open(file_name, 'w', newline='') as file:
            file.writelines(sorted(file_lines))

        if verbose:
            print('The local variable "%s" setted to the value "%s"' % (local_variable, local_variable_value))
        os.environ[local_variable] = local_variable_value
    if exit_on_complete:
        exit()

    return local_variable_value


def change_to_clis_dir(cli=''):
    os.chdir(get_clis_dir(cli))


def get_clis_dir(cli):
    return os.path.join(os.getenv('CLI_PATH'), 'clis', cli)


def write_docker_compose(project_dir, services=None, volumes=None, ports=None):
    if ports is None:
        ports = []

    if volumes is None:
        volumes = []

    if services is None:
        services = []

    file_name = os.path.join(project_dir, 'docker-compose.yml')

    if project_dir == '.':
        project_dir = os.getcwd().split('/')[-1]

    volumes.append('.:/' + project_dir)
    volumes.append(project_dir + '_root:/root')
    volumes_list = [
        project_dir + '_root'
    ]

    services_dict = {
        project_dir: {
            'build': {'context': '.'},
            'command': 'bash -c "while true; do sleep 60; done"',
            'container_name': project_dir,
            'volumes': volumes
        }
    }

    if ports:
        services_dict[project_dir]['ports'] = ports

    for s in services:
        if s == 'postgres':
            services_dict['postgres'] = {
                'image': 'postgres:11',
                'container_name': project_dir + '_postgres',  # TODO parametrizar
                'environment': {
                    'POSTGRES_PASSWORD': 'postgres'  # TODO parametrizar
                },
                'volumes': ['postgres:/var/lib/postgresql/data']  # TODO parametrizar
            }
            volumes_list.append('postgres')
            services_dict[project_dir]['depends_on'] = ['postgres']

    with open(file_name, 'w') as file:
        yaml.dump({'version': '3'}, file)
        file.write('\n')
        yaml.dump({'services': services_dict}, file)
        file.write('\n')
        yaml.dump({'volumes': {v: None for v in volumes_list}}, file)

    replace_in_file(file_name, ': null', ':')


def replace_in_file(file_name, old, new):
    with open(file_name, 'r') as old_file:
        old_info = old_file.read()

    with open(file_name, 'w') as new_file:
        new_file.write(old_info.replace(old, new))
