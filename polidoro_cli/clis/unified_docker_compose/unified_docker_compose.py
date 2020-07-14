import os

from polidoro_argument import Command
from polidoro_cli.clis.cli import CLI
from polidoro_cli.clis.cli_utils import set_environment_variables, CONFIG_FILE
from polidoro_cli.clis.docker.docker import Docker


class UnifiedDockerCompose(CLI):
    help = 'UnifiedDockerCompose CLI commands'

    @staticmethod
    @Command(
        help='Run "docker-compose up"'
    )
    def up(*args):
        compose_args, other_args = UnifiedDockerCompose._split_args(args)
        udc_dir = UnifiedDockerCompose._get_udc_dir()
        CLI.execute('docker-compose up %s %s %s' % (compose_args, Docker.get_container_name(), other_args),
                    dir=udc_dir)

    @staticmethod
    @Command(
        help='Run "docker-compose down"'
    )
    def down(*args):
        compose_args, other_args = UnifiedDockerCompose._split_args(args)
        udc_dir = UnifiedDockerCompose._get_udc_dir()
        CLI.execute('docker-compose down %s %s' % (compose_args, other_args),
                    dir=udc_dir)

    @staticmethod
    @Command(
        help='Restart the container'
    )
    def restart(*args):
        Docker.stop()
        UnifiedDockerCompose.up(*args)

    @staticmethod
    def _split_args(args):
        compose_args = ' '.join(filter(lambda a: a.startswith('-'), args))
        other_args = ' '.join(filter(lambda a: not a.startswith('-'), args))
        return compose_args, other_args

    @staticmethod
    def _get_udc_dir():
        udc_dir = os.environ.get('UNIFIED_DOCKER_COMPOSE_DIR', None)
        if udc_dir and not os.path.exists(udc_dir):
            print('%s is not a valid directory' % udc_dir)
            udc_dir = None
        if not udc_dir:
            udc_dir = set_environment_variables(
                'UNIFIED_DOCKER_COMPOSE_DIR',
                input('UnifiedDockerCompose dir: '),
                file_name=CONFIG_FILE,
                exit_on_complete=False)
        return udc_dir
