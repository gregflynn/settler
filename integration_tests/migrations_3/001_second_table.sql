-- @DO
CREATE TABLE testy (
    a VARCHAR(1) PRIMARY KEY
);
ALTER TABLE testy ADD COLUMN b VARCHAR(10);

-- @UNDO
DROP TABLE testy;
