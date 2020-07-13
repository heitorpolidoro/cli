import os

CONFIG_FILE = os.path.expanduser('~/.cli/config')
LOCAL_ENV_FILE = os.path.expanduser('~/.cli/%s.env' % os.getcwd().replace('/', '-'))


def load_environment_variables(file_name):
    # Load local environment variables
    if os.path.exists(file_name):
        with open(file_name, 'r', newline='') as file:
            for line in file.readlines():
                name, value = line.split('=')
                os.environ[name] = value.strip()


def set_environment_variables(local_variable, local_variable_value=None, file_name=LOCAL_ENV_FILE, verbose=True,
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
