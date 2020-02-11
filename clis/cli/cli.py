import os

from argument import Command


class CLI(object):

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
    # @classmethod
    # def wrapper(cls, name, cmd, **kwargs):
    #     def wrapper_(*args, **_kwargs):
    #         kwargs.update(_kwargs)
    #         cls.execute(cmd, *args, **kwargs)
    #
    #     setattr(wrapper_, '__name__', name)
    #     return wrapper_
    #
    @classmethod
    def execute(cls, command, *args, docker=False, environment_vars={}):
        command = ' '.join([command] + list(args))
        if docker:
            from clis.docker.docker import Docker
            Docker.exec(command, environment_vars=environment_vars)
        else:
            if environment_vars:
                command = ' '.join(['%s=%s' % (name, value) for name, value in environment_vars.items()] + [command])
            print('+ %s' % command)
            os.system(command)
