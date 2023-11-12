#! /bin/bash

psql -U postgres -h localhost -d postgres \
    -c "DROP DATABASE settler" \
    -c "DROP ROLE settler"
