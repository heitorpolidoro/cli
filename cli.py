# TODO
# Incluir
# - comandos docker
# - comandos de migração de bd
# - comandos do dev.sh
# - comandos do git
# bash completion

from argparse import SUPPRESS

from parser import Parser

parser = Parser()

parser.add_packages()
parser.add_argument('--set-local-variable', action='store', type=Parser.set_local_variable,
                    metavar='NAME=VALUE', help='set a local variable value')
parser.add_argument('--install', action='store', type=Parser.install,
                    metavar='PACKAGE', help='install a PACKAGE')
parser.add_argument('--uninstall', action='store', type=Parser.uninstall,
                    metavar='PACKAGE', help='uninstall a PACKAGE')
parser.add_argument('--update', action='store', nargs='?', type=Parser.update, const='all',
                    metavar='PACKAGE', help='update the PACKAGE and all installed packages')
parser.add_argument('--install_all_default_packages', action='store', nargs='?',
                    type=Parser.install_all_default_packages, const='all',
                    metavar='PACKAGE', help=SUPPRESS)


parser.parse_args()
