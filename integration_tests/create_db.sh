#! /bin/bash

psql -d postgres \
    -c "CREATE USER settler WITH password 'settlertest'" \
    -c "CREATE DATABASE settler" \
    -c "GRANT ALL PRIVILEGES ON DATABASE settler TO settler;"
