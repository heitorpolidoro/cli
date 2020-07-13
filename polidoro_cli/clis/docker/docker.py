import os

from polidoro_argument import Command
from polidoro_cli.clis.cli import CLI


class Docker(CLI):
    help = 'Docker CLI commands'
    _container_name = None

    @staticmethod
    def get_container_name():
        if Docker._container_name is None:
            container_name_key = os.getcwd() + '_CONTAINER_NAME'
            Docker._container_name = os.getenv(container_name_key, os.getcwd().split('/')[-1])
        return Docker._container_name

    @staticmethod
    @Command(
        help='Run "docker exec COMMAND"',
        aliases={'environment_vars': 'e'}
    )
    def exec(*args, environment_vars={}):
        if isinstance(environment_vars, str):
            env_vars = environment_vars
        else:
            env_vars = ' '.join('%s=%s' % (key, value) for key, value in environment_vars.items())

        if env_vars:
            env_vars = ' -e ' + env_vars
        CLI.execute('docker exec%s -it %s %s' % (
            env_vars,
            Docker.get_container_name(),
            ' '.join(args)
        ))

    @staticmethod
    @Command(
        help='Run "docker-compose up"'
    )
    def up(*args):
        CLI.execute('docker-compose up %s' % ' '.join(args))

    @staticmethod
    @Command(
        help='Run "docker-compose down"'
    )
    def down(*args):
        CLI.execute('docker-compose down %s' % ' '.join(args))

    @staticmethod
    @Command(
        help='Run "docker stop"'
    )
    def stop(*args):
        CLI.execute('docker stop %s %s' % (Docker.get_container_name(), ' '.join(args)))

    @staticmethod
    @Command(
        help='Run "docker logs'
    )
    def logs(*args):
        CLI.execute('docker logs %s %s' % (Docker.get_container_name(), ' '.join(args)))

