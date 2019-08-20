import atexit
import os
import re
import sys

from requests import HTTPError

from requests_utils import Requests


class UtilsStdout(object):
    """
    Print wrapper to clear to end of line on every print and count the number of printed lines to return and allow
    monitoring prints
    """
    def __init__(self):
        self.stdout = sys.stdout
        self.lines = 0

    def __getattr__(self, item):
        return getattr(self.stdout, item)

    def write(self, text):
        print(text, end=Clear_to_end_of_line, file=self.stdout)
        # Count every '\n' (new line)
        self.lines += text.count('\n')

    def flush(self):
        self.stdout.flush()

    def return_printed_lines(self, clear=True):
        """
        Return the number os new lines

        :param clear: To clear to the end of screen before return lines
        """
        if self.lines:
            return_lines(self.lines)
            os.system('tput cub $(tput cols)')
            if clear:
                clear_to_end_of_screen()
        self.lines = 0

    def reset_printed_lines(self):
        """ Reset the number os new lines to start count from now """
        self.lines = 0


sys.stdout = UtilsStdout()


Clear_to_end_of_line = os.popen("tput el").read()


def run(command):
    """
    Run a command line command

    :param command: Command to execute

    :return: return code, output
    """
    import subprocess

    resp = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    out, err = resp.communicate()
    errorcode = resp.returncode
    if errorcode:
        exit(err)

    return errorcode, out.strip()


def run_and_return_output(command):
    """
    Run a command line command and return only the output

    :param command: Command to execute

    :return: output
    """
    return run(command)[1]


def template_safe_substitute(target, **kwargs):
    """
    Safe substitute ${NAME} values in strings.
    First lookup in the kwargs, then in the environment variables

    :param target: To object to substitute
    :param kwargs: Values to substitute
    :return:
    """
    if isinstance(target, tuple):
        return tuple(
            template_safe_substitute(a, **kwargs)
            for a in target
        )
    elif isinstance(target, list):
        return [
            template_safe_substitute(a, **kwargs)
            for a in target
        ]

    elif isinstance(target, dict):
        return {
            k: template_safe_substitute(v, **kwargs)
            for k, v in target.items()
        }

    elif isinstance(target, (str, bytes)):
        from string import Template
        for var in re.findall("\${(\w+)}", target):
            if var not in kwargs:
                kwargs[var] = get_env_var(var)

        return Template(target).safe_substitute(**kwargs)
    else:
        return target


def convert_duration(duration):
    """ Convert a duration in seconds to Xm Ys """
    if duration is not None:
        converted_duration = ''
        minutes = duration / 60
        seconds = duration % 60
        if minutes > 0:
            converted_duration += '%dm ' % minutes
        converted_duration += '%ds' % seconds
        return converted_duration
    return ''


def get_env_var(name, default=None):
    """ Get an environment variable, if there is none raise an exception """
    resp = os.getenv(name, default)
    if resp is None:
        cli_name = os.getenv('CLI_NAME')
        raise EnvironmentError('There is no environment variable called "%s"!\n'
                               'Export the variable or use "%s --set-local-variable=%s=VALUE" '
                               'to save the value locally.' % (name, cli_name, name))
    return resp


def validate_env_var(name, default=None, message=None):
    """
    Validate if an environment variable is available

    :param name: Name of the environment variable
    :param default: Default value if the environment variable is not available
    :param message: Message in case the variable is not available and default is None
    :return:
    """
    try:
        get_env_var(name)
    except EnvironmentError as e:
        if default is not None:
            if callable(default):
                default = default()
            os.environ[name] = str(default)
        else:
            if message:
                message = '\n' + message
            exit('%s.%s' % (e.args[0], message))


def get_current_branch():
    return run_and_return_output('git rev-parse --abbrev-ref HEAD')


def reset_printed_lines():
    sys.stdout.reset_printed_lines()


def return_lines(lines=1):
    os.system('tput cuu %d' % lines)


def return_printed_lines(clear=True):
    sys.stdout.return_printed_lines(clear)


def notify(title, message='', expire_time=1000, icon=''):
    os.system('notify-send --expire-time=%d --icon=%s "%s" "%s"' % (expire_time, icon, title, message))


def clear_to_end_of_screen():
    os.system('tput ed')


def hide_cursor():
    os.system('setterm -cursor off')
    atexit.register(show_cursor)


def show_cursor():
    os.system('setterm -cursor on')
    atexit.unregister(show_cursor)


def get_last_local_commit(branch=None):
    if branch is None:
        branch = get_current_branch()
    return run_and_return_output('git log --pretty=%%H -1 %s' % branch)


def get_last_github_commit(branch=None):
    if branch is None:
        branch = get_current_branch()
    resp = run_and_return_output('git ls-remote origin %s' % branch).split()
    if resp:
        return resp[0]


def get_last_gitlab_commit(branch=None):
    if branch is None:
        branch = get_current_branch()

    # Replacing any '/' into '%2F'
    branch = branch.replace('/', '%2F')

    try:
        content = Requests.get_content(
            'https://gitlab.com/api/v4/projects/${GITLAB_PROJECT}/repository/commits/%s' % branch,
            headers={'PRIVATE-TOKEN': '${PRIVATE_TOKEN}'})
        return content['id']
    except HTTPError as e:
        if e.response.status_code == 404:
            pass
        else:
            raise


def get_gitlab_project_id(project_name):
    content = Requests.get_content('https://gitlab.com/api/v4/projects?search=%s&simple=true' % project_name,
                                   headers={'PRIVATE-TOKEN': '${PRIVATE_TOKEN}'})
    if isinstance(content, list):
        exit('Project "%s" not found in GitLab' % project_name)
    if content:
        return content['id']
