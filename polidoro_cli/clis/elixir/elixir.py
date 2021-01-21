import os
from string import Template

from polidoro_argument import Command

from polidoro_cli.clis.cli_utils import get_clis_dir, write_docker_compose, replace_in_file
from polidoro_cli.clis.cli import CLI


class Elixir(CLI):
    help = 'Elixir CLI commands'

    def __init__(self):
        super(Elixir, self).__init__(
            commands={
                'compile': 'mix compile',
                'credo': 'mix credo',
                'deps': 'mix deps.get',
                'iex': 'iex -S mix',
                'iexup': 'iex -S mix phx.server',
                'test': {'cmd': 'mix test', 'environment_vars': {'MIX_ENV': 'test'}},
                'setup': 'mix ecto.setup',
                'reset': 'mix ecto.reset',
                'migrate': 'mix ecto.migrate',
                'up': 'mix phx.server',
                'schema': 'mix phx.gen.schema',
                'gettext': 'mix gettext.extract --merge',
            },
            aliases={'docker': 'd'},
            helpers={'docker': 'if is to run in the docker container'},
            command_help={'test': 'Run "MIX_ENV=test mix test"'},
        )

    @classmethod
    def wrapper(cls, name, cmd, **kwargs):
        def wrapper_(*args, docker=False, **_kwargs):
            kwargs.update(_kwargs)
            Elixir.execute(cmd, *args, docker=docker, **kwargs)

        setattr(wrapper_, '__name__', name)
        return wrapper_

    @staticmethod
    @Command(
        help='Run "mix phx.new"',
        aliases={
            'docker': 'd',
            'docker_compose': 'c'
        },
        helpers={
            'docker': 'Create the Dockerfile',
            'docker_compose': 'Create the docker-compose file'
        }
    )
    def new(project_dir, *args, docker=False, docker_compose=False, postgres=False):
        CLI.execute("mix phx.new --verbose", project_dir, *args)

        # creating docker-compose.yml
        if docker_compose:
            docker = True
            services = []
            if postgres:
                services.append('postgres')
                replace_in_file(
                    os.path.join(project_dir, 'config/dev.exs'),
                    'hostname: "localhost"', 'hostname: "%s_postgres"' % project_dir)
                replace_in_file(
                    os.path.join(project_dir, 'config/test.exs'),
                    'hostname: "localhost"', 'hostname: "%s_postgres"' % project_dir)
            write_docker_compose(project_dir, services=services, ports=['4000:4000'])

        # creating Dockerfile
        if docker:
            Elixir.create_file(project_dir, 'Dockerfile')

    @staticmethod
    def create_file(project_dir, file_name):
        with open(os.path.join(get_clis_dir('elixir'), file_name), 'r') as template:
            with open(os.path.join(project_dir, file_name), 'w') as file:
                if project_dir == '.':
                    project_dir = os.getcwd().split('/')[-1]
                file.write(Template(''.join(template.readlines())).safe_substitute(
                    project_dir=project_dir,
                    project_dir_root=project_dir + '_root'))


Elixir()
