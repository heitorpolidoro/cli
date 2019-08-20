import inspect
import json
from argparse import ArgumentParser

from loading import Loading
from parser.command import Command
from utils import *

__version__ = '0.0.1-beta'

# Only works on Python 3. Why? Because I want.
if sys.version_info[0] < 3:
    raise Exception('Must be using Python 3')

ENV_FILE = os.path.expanduser('~/.cli/%s.env' % os.getcwd().replace('/', '-'))
CONFIG_FILE = os.path.expanduser('~/.cli/config')


class Parser(ArgumentParser):
    """
    A ArgumentParser wrapper to create subparsers for the @Command

    Use:
        parser = Parser(<arguments>)

        parser.add_argument(Class) # Class with function decorated with @Command
        parser.add_argument(function) # Function decorated with @Command

        arguments = parser.parse_args()
    """

    def __init__(self, *args, version=__version__, **kwargs):
        kwargs.setdefault('prog', get_env_var('CLI_NAME'))
        super().__init__(*args, **kwargs)

        if version:
            self.add_argument('-v', '--version', action='version', version='%(prog)s ' + version)
        self.subparsers = None

    def add_subparsers(self, **kwargs):
        """ Add subparsers if not exists """
        if self.subparsers is None:
            metavar = kwargs.get('metavar', 'command')
            required = kwargs.get('required', True)
            self.subparsers = super(Parser, self).add_subparsers(
                metavar=metavar,
                required=required,
                **kwargs
            )

        return self.subparsers

    # noinspection PyMethodOverriding
    def add_argument(self, dest, *args, **kwargs):
        if isinstance(dest, type):
            # if the argument is a class
            clazz = dest
            command_functions = self._get_command_functions(clazz)
            clazz_name = clazz.__name__
            if command_functions:
                subparsers = self.add_subparsers()

                subparser = subparsers.add_parser(clazz_name.lower(), help=getattr(clazz, 'help', None),
                                                  version=getattr(clazz, 'version', None))
                # Add a subparser recursively for each function decorated with @Commad
                for command in command_functions:
                    # noinspection PyTypeChecker
                    subparser.add_argument(command)
            else:
                raise TypeError('There is not any method decorated with @Command in the class "%s"', clazz_name)

        elif isinstance(dest, Command):
            # if the argument is a function
            command = dest
            subparsers = self.add_subparsers()
            subparser = subparsers.add_parser(command.name, help=command.help)
            for arg in command.arguments:
                subparser.add_argument(*arg.arguments, **arg.kwargs)

            subparser.set_defaults(func=command)
        else:
            super(Parser, self).add_argument(dest, *args, **kwargs)

    def parse_args(self, *args, **kwargs):
        arguments = super(Parser, self).parse_args(*args, **kwargs)

        if hasattr(arguments, 'func'):
            # If has the func attribute, is a function to be called
            if inspect.signature(arguments.func).parameters:
                # If the function accept parameters, pass arguments as parameter
                arguments.func(arguments)
            else:
                arguments.func()
        return arguments

    @staticmethod
    def _get_command_functions(clazz):
        """ Return all functions deocrated with @Command from the class"""
        resp = []
        for v in vars(clazz):
            if not v.startswith('_'):
                method = getattr(clazz, v)
                if isinstance(method, Command):
                    resp.append(method)
        return resp

    @staticmethod
    def load_local_environment_variables(file=ENV_FILE):
        # Load local environment variables
        if os.path.exists(file):
            with open(file, 'r', newline='') as arq:
                for line in arq.readlines():
                    name, value = line.split('=')
                    os.environ[name] = value.strip()

    @staticmethod
    def set_local_variable(local_variable, file=ENV_FILE, verbose=True, exit_on_complete=True):
        if local_variable:
            if '=' not in local_variable or local_variable.endswith('='):
                raise SyntaxError('--set-local-variable must be in the format NAME=VALUE')

            name, value = local_variable.split('=')
            if os.path.exists(file):
                with open(file, 'r', newline='') as arq:
                    file_lines = arq.readlines()
            else:
                file_lines = []

            for line in file_lines:
                if line.startswith(name + '='):
                    file_lines.remove(line)
                    break

            file_lines.append(name + '=' + value)

            with open(file, 'w', newline='') as arq:
                arq.writelines(sorted(file_lines))

            if verbose:
                print('The local variable "%s" setted to the value "%s"' % (name, value))
        os.environ[name] = value
        if exit_on_complete:
            exit()

    @staticmethod
    def install(package, validate=True, verbose=True, exit_on_complete=True):
        installed_packages = json.loads(get_env_var('INSTALLED_PACKAGES', '[]'))
        if validate and package in installed_packages:
            exit('Package %s already installed' % package)

        Loading.start()
        if verbose:
            print('Installing %s...' % package)

        if package not in installed_packages:
            installed_packages.append(package)
        Parser.set_local_variable('INSTALLED_PACKAGES=%s' % json.dumps(installed_packages),
                                  file=CONFIG_FILE, verbose=False, exit_on_complete=False)

        if verbose:
            return_printed_lines()
            print('%s installed successfully' % package)

        if exit_on_complete:
            exit()

    @staticmethod
    def uninstall(package):
        installed_packages = json.loads(get_env_var('INSTALLED_PACKAGES', '[]'))
        if package not in installed_packages:
            exit('Package %s is not installed' % package)

        Loading.start()
        print('Uninstalling %s...' % package)

        installed_packages.remove(package)
        Parser.set_local_variable('INSTALLED_PACKAGES=%s' % json.dumps(installed_packages),
                                  file=CONFIG_FILE, verbose=False, exit_on_complete=False)
        try:
            Parser.update(verbose=False, exit_on_complete=False)
        except Exception:
            installed_packages.append(package)
            Parser.set_local_variable('INSTALLED_PACKAGES=%s' % json.dumps(installed_packages),
                                      file=CONFIG_FILE, verbose=False, exit_on_complete=False)
            raise

        return_printed_lines()
        print('%s uninstalled successfully' % package)
        exit()

    @staticmethod
    def update(package='all', verbose=True, exit_on_complete=True):
        Loading.start()

        os.chdir(get_env_var('CLI_PATH'))
        if verbose:
            print('Updating CLI')
        run('git stash')
        run('git pull')
        run('git stash pop')

        for package in json.loads(get_env_var('INSTALLED_PACKAGES', '[]')):
            Parser.install(package, validate=False, verbose=False, exit_on_complete=False)

        if verbose:
            return_printed_lines()
            print('PACKAGE updated successfully')

        if exit_on_complete:
            exit()

    def add_packages(self):
        for package in json.loads(get_env_var('INSTALLED_PACKAGES', '[]')):
            package = __import__(package)
            for name in dir(package):
                obj = getattr(package, name)
                if isinstance(obj, type):
                    self.add_argument(obj)


Parser.load_local_environment_variables(CONFIG_FILE)
Parser.load_local_environment_variables()
