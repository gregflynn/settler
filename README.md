# settler
Settler is a simple migration framework for Flask, SQLAlchemy, and Flask-SQLAlchmey.

```python
from settler import MigrationManager

# if you're using SQLAlchemy
from sqlalchemy import create_engine
engine = create_engine("db connection url", client_encoding='utf8')

# if you're using flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
engine = SQLAlchemy({ ... }).engine

migration_manager = MigrationManager(engine, migrations_dir='migrations')

#
# Check the database and migrations folder highest versions and print them
#
migration_manager.check()

#
# Bring your db up to the highest revision from the migrations folder
#
migration_manager.update()

#
# Undo the last migration applied
#
migration_manager.undo()
```

000_create_user.sql:
```sql
-- @DO
CREATE TABLE IF NOT EXISTS users (
  uid SERIAL PRIMARY KEY,
  email VARCHAR(100) UNIQUE,
  hashed_password VARCHAR(120)
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- @UNDO
DROP TABLE IF EXISTS users;
DROP INDEX IF EXISTS idx_users_email;
```
