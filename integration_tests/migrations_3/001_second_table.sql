-- @DO
CREATE TABLE second_table (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    active BOOLEAN DEFAULT FALSE
);

-- @UNDO
DROP TABLE second_table;
