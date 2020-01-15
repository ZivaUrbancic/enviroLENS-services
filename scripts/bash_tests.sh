#!/bin/sh
# file: scripts/validate.sh

# This script catches some of the bugs that cannot be cought
# with pylint, pytest or other testing frameworks.

testFilesWithPrint() {
    # count the number of print statements in the file
    # The number of print statements should be 0
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