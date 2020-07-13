#!/usr/bin/env bash
python_cmd='python3'
if [[ -z "$(which python3)" ]]; then
  python_cmd='python3'
  if [[ -z "$(which python3)" ]] || [[ $(python3 -c 'import sys; print(sys.version_info[1])') -lt 7 ]]; then
    echo "CLI works only in Python 3. o you want to install?[Y/n]"
    read -r resp

    SUDO=''
    if [[ -n "$(which sudo)" ]]; then
            SUDO='sudo'
    fi

    if [[ -z ${resp} ]] || [[ "${resp}" == "y" ]] || [[ "${resp}" == "Y" ]]; then
      $SUDO apt-get update
      $SUDO apt-get install -y python3 python3-pip || exit 1
    else
      exit 1
    fi
  fi
fi

${python_cmd} -m pip install -r requirements.txt --user || exit 1

#echo -e '\nQual nome deseja para o CLI':
#read -r NAME
NAME=cli
if [[ -z "${NAME}" ]]; then
  echo "O nome é obrigatório"
  exit 1
fi

echo "#!/usr/bin/env bash" > "${NAME}"
echo "${python_cmd} ${PWD}/cli \"\$@\""  >> "${NAME}"
chmod +x "${NAME}"

if ! grep -q "${PWD}" ~/.bashrc; then
  echo "export PATH=\"${PWD}:\$PATH\"" >> ~/.bashrc
fi

mkdir ~/.cli

#echo "CLI_NAME=${NAME}" > ~/.cli/config
echo "CLI_PATH=${PWD}" > ~/.cli/config

#${python_cmd} "${PWD}"/cli --install_all_default_packages

echo -e '\nRun "source ~/.bashrc" to update the PATH'
