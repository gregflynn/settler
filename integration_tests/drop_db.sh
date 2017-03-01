#! /bin/bash

psql -d postgres \
    -c "DROP DATABASE settler" \
    -c "DROP ROLE settler"
