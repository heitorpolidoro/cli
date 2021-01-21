import os
from string import Template

from polidoro_argument import Command

from polidoro_cli.clis.cli_utils import get_clis_dir, write_docker_compose, replace_in_file
from polidoro_cli.clis.cli import CLI


class Ruby(CLI):
    help = 'Ruby CLI commands'

    def __init__(self):
        super(Ruby, self).__init__(
            commands={
                'console': 'bundle exec rails console',
                'migrate': 'bundle exec rails db:migrate',
                'create': 'bundle exec rails db:create'
            },
            aliases={'docker': 'd'},
            helpers={'docker': 'if is to run in the docker container'},
            command_help={'test': 'Run "MIX_ENV=test mix test"'},
        )

    @classmethod
    def wrapper(cls, name, cmd, **kwargs):
        def wrapper_(*args, docker=False, **_kwargs):
            kwargs.update(_kwargs)
            Ruby.execute(cmd, *args, docker=docker, **kwargs)

        setattr(wrapper_, '__name__', name)
        return wrapper_

Ruby()
