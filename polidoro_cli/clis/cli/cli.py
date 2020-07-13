"""
Module doc sctring
"""
import os

from polidoro_argument import Command


class CLI:
    """
    Parent class for CLI classes
    """

    def __init__(self, commands={}, aliases={}, helpers={}, command_help={}):
        for name, cmd in commands.items():
            if isinstance(cmd, dict):
                kwargs = cmd
            else:
                kwargs = {'cmd': cmd}

            Command(
                aliases=aliases,
                helpers=helpers,
                help=command_help.get(name, 'run %s' % kwargs['cmd']),
                method_name=name
            )(self.__class__.wrapper(name, **kwargs))

    @classmethod
    def wrapper(cls, name, cmd, **kwargs):
        raise NotImplemented

    @classmethod
    def execute(cls, command, *args, docker=False, environment_vars={}, dir=None):
        command = ' '.join([command] + list(args))
        if docker:
            from polidoro_cli.clis.docker.docker import Docker
            Docker.exec(command, environment_vars=environment_vars)
        else:
            if environment_vars:
                command = ' '.join(['%s=%s' % (name, value) for name, value in environment_vars.items()] + [command])
            print('+ %s' % command)
            if dir:
                os.chdir(dir)
            os.system(command)
