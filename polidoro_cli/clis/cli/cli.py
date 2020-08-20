"""
Module doc sctring
"""
import os

from polidoro_argument import Command


class CLI:
    """
    Parent class for CLI classes
    """

    def __init__(self, commands=None, aliases=None, helpers=None, command_help=None):
        if commands is None:
            commands = {}
        if aliases is None:
            aliases = {}
        if helpers is None:
            helpers = {}
        if command_help is None:
            command_help = {}
        for name, cmd in commands.items():
            if isinstance(cmd, dict):
                kwargs = cmd
            else:
                kwargs = {'cmd': cmd}

            Command(
                aliases=aliases,
                helpers=helpers,
                help=command_help.get(name, 'Run "%s"' % kwargs['cmd']),
                method_name=name
            )(self.__class__.wrapper(name, **kwargs))

    @classmethod
    def wrapper(cls, name, cmd, **kwargs):
        raise NotImplemented

    @classmethod
    def execute(cls, command, *args, docker=False, environment_vars=None, dir=None):
        if environment_vars is None:
            environment_vars = {}
        command = ' '.join([command] + list(args))
        if docker:
            from polidoro_cli.clis.docker.docker import Docker
            Docker.exec(command, environment_vars=environment_vars)
        else:
            if environment_vars:
                command = ' '.join(
                    ['%s=%s' % (name, value) for name, value in environment_vars.items()] + [command]
                )
            print('+ %s' % command)
            if dir:
                os.chdir(dir)
            os.system(command)
