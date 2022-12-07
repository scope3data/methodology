#!/bin/bash

TEST_DIR="test_defaults"
DEFAULTS_DIR="defaults"

# Compute the latest defaults
mkdir $TEST_DIR
python ./scope3_methodology/cli/compute_defaults.py -d $TEST_DIR

# Verify we have the identical number of default files
TEST_DEFAULT_FILE_COUNT=$(ls ${TEST_DIR} | wc -l)
DEFAULT_FILE_COUNT=$(ls ${DEFAULTS_DIR} | wc -l)

if [ "$TEST_DEFAULT_FILE_COUNT" -ne "$DEFAULT_FILE_COUNT" ]; then
    echo "Number of default files does not match checked in files. Verify, update, and check-in computed default files." && exit 1
fi

# Verify the default files is the checked in file
for test_default_file in $TEST_DIR/*;
do
    checked_in_default_file=${DEFAULTS_DIR}/$(basename $test_default_file)
    if ! diff <(yq -P .defaults "$checked_in_default_file") <(yq -P  .defaults  "$test_default_file") ; then
        echo "$test_default_file differs from $checked_in_default_file. Verify, update, and check-in computed default files." && exit 1
    fi
done

rm -rf $TEST_DIR