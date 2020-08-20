# TODO
# bash completion
import glob
import os

from polidoro_argument import ArgumentParser

if __name__ == '__main__':
    import sys
    sys.path.append("/mnt/c/Users/heito/IdeaProjects/cli/")

from polidoro_cli.clis.cli_utils import load_environment_variables, CONFIG_FILE, LOCAL_ENV_FILE, change_to_clis_dir

load_environment_variables(CONFIG_FILE)
load_environment_variables(LOCAL_ENV_FILE)

VERSION = '0.1.2'


def load_clis():
    cur_dir = os.getcwd()
    change_to_clis_dir()
    for d in os.listdir():
        if os.path.isdir(d) and not d.startswith('__'):
            try:
                os.chdir(d)
                for file in glob.glob('*.py'):
                    __import__('polidoro_cli.clis.%s.%s' % (d, file.replace('.py', '')))
            except SystemExit as e:
                print(e)
        change_to_clis_dir()
    os.chdir(cur_dir)


def main():
    # Load all the CLIs
    load_clis()

    ArgumentParser(version=VERSION).parse_args()


if __name__ == '__main__':
    os.environ['CLI_PATH'] = os.path.dirname(os.path.realpath(__file__))
    if os.environ.get('OS', None) == 'Windows_NT':
        os.environ['CLI_PATH'] = os.environ['CLI_PATH'].replace('/mnt/c', 'C:').replace('/', '\\')

    main()
