#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"/client

python setup.py sdist bdist_wheel
mkdir ../../output
tar -xvf ./dist/*.tar.gz --strip-components=1 -C ../../output/
