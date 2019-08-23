import atexit
import inspect
import types


class Command(object):
    """
    Decorator to configure a command line method.
    Use:

    @Command
    def foo():
        <code>

    Will create the command: "<CLI_NAME> foo" calling the function foo

    @Command(
        # The parameters to CommandArgument are the same for argparse.ArgumentParser.add_argument
        arguments=[CommandArgument('--bar')] # Must be a list
    )
    def foo(arguments):
        print(arguments.bar)

    Will create the command: "<CLI_NAME> foo --bar=value" calling the function foo passing the value of bar

    Class Foo():
        help=<help string to show when --help is used>
        @staticmethod # Must be static
        @Command
        def bar():
            <code>

    Will create the command: "<CLI_NAME> foo bar" calling the function Foo.bar
    """
    def __init__(self, *args, function=None, arguments=None, help=None, **_):
        if args:
            if isinstance(args[0], types.FunctionType):
                function = args[0]
                args = list(args)
                args.pop(0)
                self.__init__(*args, function=function)
            else:
                raise TypeError('Command only accepts named parameters')

        if arguments is None:
            arguments = {}
        elif not isinstance(arguments, list):
            raise TypeError('The "arguments" parameter must be a list ')

        self.function = None
        self.name = None
        self.arguments = arguments
        self.help = help

        if isinstance(function, types.FunctionType):
            if arguments and (not inspect.signature(function).parameters or
                              'arguments' != list(inspect.signature(function).parameters)[0]):
                raise TypeError('The first argument of the function "%s" must be "arguments"' % function.__name__)
            self.function = function
            self.name = function.__name__

    def __call__(self, *args, **kwargs):
        if self.function is None:
            # When decorate with arguments a method
            func_kwargs = self.__dict__
            func_kwargs['function'] = args[0]

            return Command(**func_kwargs)
        else:
            # When the method is called
            try:
                self.function(*args, **kwargs)
            except KeyboardInterrupt:
                pass
            except Exception:
                from helpers.utils import return_printed_lines
                atexit.unregister(return_printed_lines)
                raise
