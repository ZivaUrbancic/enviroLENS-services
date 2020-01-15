#!/bin/sh
# file: scripts/validate_python_prints.sh

# this script checks the number of print statements
# found in the python code. We want to avoid printing
# out parts of the code and should use logs or throwing
# errors to signify or show the errors

testFilesWithPrint() {
    # count the number of print statements in the file
    FILES_WITH_PRINT=$(grep -Rwl --exclude-dir=static --exclude-dir=scripts "print" ./*)
    FILES_COUNT=$(echo "$FILES_WITH_PRINT" | wc -l)

    if [ $FILES_COUNT != 0 ]; then
        printf '========================= ERROR =========================\n'
        printf 'Number of "print" statements in files: %s\n' $FILES_COUNT
        printf 'Files with "print" statements in project:\n'
        printf "$FILES_WITH_PRINT"
        printf '\n'
    fi

    assertEquals 0 $FILES_COUNT
}

# load shunit2
. ./scripts/shunit2-2.1.6/src/shunit2