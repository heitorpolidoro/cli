# TODO
# - comandos default?

# Instalar comandos
# cli install
# - perguntar pelo nome
# - colocar o nome no PATH
# - parser = Parser('${NOME}')
# cli install gitlab
# - faz o cherry pick da HEAD da branch gitlab
# - parser.add_argumento(Pipeline)
# cli update
# -- atualiza todos os repositório e refaz os cherry picks

# Incluir
# - comandos docker
# - comandos de migração de bd
# - comandos do dev.sh
# - comandos do git

# bash completion
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


parser.parse_args()
