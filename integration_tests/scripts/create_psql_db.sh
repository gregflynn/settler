#! /bin/bash

psql -U postgres -h localhost -d postgres \
    -c "CREATE USER settler WITH password 'settlertest'" \
    -c "CREATE DATABASE settler" \
    -c "GRANT ALL PRIVILEGES ON DATABASE settler TO settler" \
    -c "ALTER DATABASE settler OWNER TO settler"
