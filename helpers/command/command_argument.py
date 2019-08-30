class CommandArgument(object):
    """
    To use with @Command.

    The arguments are the same as argparse.ArgumentParser.add_argument
    """
    def __init__(self, *arguments, **kwargs):
        self.arguments = arguments
        self.kwargs = kwargs
