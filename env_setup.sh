#!/usr/bin/env bash

function try_pip_install(){
  if command -v dnf
  then
    echo "installing pip via dnf"
    sudo dnf install python3-virtualenv
    return 0
  elif command -v apt
  then
    echo "attempting to install pip via apt"
    sudo apt install python3-virtualenv
    return 0
  else
    return 1
  fi
}

if ! command -v pip
then
  echo "attempting to install pip"
  if ! try_pip_install
  then
    echo "dnf, apt not found, please install pip for python3"
    exit
  fi
  echo "python3 successfully installed"
fi


virtualenv -m venv env
source "env/bin/activate"
pip install -r requirements.txt
