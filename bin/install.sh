#!/usr/bin/env bash

install_dir=`pwd`

pipcmd=`which pip`

if [ "${pipcmd}" == "" ]; then
  printf "Python package manager 'pip' not found! Aborting...\n" 1>&2
  exit 1
fi

${pipcmd} install -r ${install_dir}/meta/requirements.txt --user
