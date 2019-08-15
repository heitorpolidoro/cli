#!/usr/bin/env bash

echo 'Qual nome deseja para o CLI':
read -r NAME

if [[ -z "${NAME}" ]]; then
  echo "O nome é obrigatório"
  exit 1
fi

echo "#!/usr/bin/env bash" > "${NAME}"
echo "python3 ${PWD}/cli.py \$*"  >> "${NAME}"
chmod +x "${NAME}"

if ! grep -q "${PWD}" ~/.bashrc; then
  echo "export PATH=\"${PWD}:\$PATH\"" >> ~/.bashrc
fi

mkdir ~/.cli > /dev/null 2>&1

source ~/.bashrc

