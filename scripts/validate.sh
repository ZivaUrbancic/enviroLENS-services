#!/bin/sh

# execute all validation scripts
DIRNAME=$(dirname $(readlink -f $0))
for f in $DIRNAME/*.sh; do
    if [[ $f == *"validate.sh"* ]]; then
        continue
    fi
    bash "$f"
done