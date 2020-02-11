# TODO
# bash completion
import glob
import os

from argument import ArgumentParser, Command

from clis.cli_utils import load_environment_variables

__version__='0.1.0'
CONFIG_FILE = os.path.expanduser('~/.cli/config')

load_environment_variables(CONFIG_FILE)
load_environment_variables()


def load_clis():
    cur_dir = os.getcwd()
    change_to_clis_dir()
    for d in os.listdir():
        change_to_clis_dir()
        if os.path.isdir(d) and not d.startswith('__'):
            try:
                os.chdir(d)
                for file in glob.glob('*.py'):
                    # print(d, '/', file)
                    __import__('clis.%s.%s' % (d, file.replace('.py', '')))
            except SystemExit as e:
                print(e)
    os.chdir(cur_dir)


def change_to_clis_dir(cli=''):
    os.chdir(os.path.join(os.getenv('CLI_PATH'), 'clis', cli))


# Load all the CLIs
load_clis()

ArgumentParser(version=__version__).parse_args()
