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

parser.add_clis()

parser.parse_args()
