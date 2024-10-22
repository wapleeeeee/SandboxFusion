#!/bin/bash
set -o errexit

py_ver="$1"
FILENAME=Miniconda3-py${py_ver//.}_23.5.2-0-Linux-x86_64.sh

if [ "$1" = "3.7" ]
then
FILENAME=Miniconda3-py${py_ver//.}_23.1.0-1-Linux-x86_64.sh
fi

wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/${FILENAME}
mkdir /root/.conda
bash ${FILENAME} -b
rm -f ${FILENAME}
