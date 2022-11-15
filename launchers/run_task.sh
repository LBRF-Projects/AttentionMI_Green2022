#!/bin/bash

cd ../$1
pipenv run klibs run $2

STATUS='running'
while [[ $STATUS == 'running' ]]; do
    sleep 1s
done
