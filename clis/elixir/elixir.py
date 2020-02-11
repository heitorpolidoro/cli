import os

from argument import Command
from clis.cli import CLI
from clis.docker.docker import Docker


class Elixir(CLI):
    help = 'Elixir CLI commands'

    def __init__(self):
        super(Elixir, self).__init__(
            commands={
                'test': {'cmd': 'mix test', 'environment_vars': {'MIX_ENV': 'test'}},
                'migrate': 'mix ecto.migrate',
                'iex': 'iex -S mix',
                'phx_server': 'mix phx.server',
                'credo': 'mix credo',
            },
            aliases={'docker': 'd'},
            helpers={'docker': 'if is to run in the docker container'},
            command_help={'test': 'run MIX_ENV=test mix test'},
        )

    @classmethod
    def wrapper(cls, name, cmd, **kwargs):
        def wrapper_(*args, docker=False, **_kwargs):
            kwargs.update(_kwargs)
            Elixir.execute(cmd, *args, docker=docker, **kwargs)

        setattr(wrapper_, '__name__', name)
        return wrapper_


Elixir()
