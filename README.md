# settler
Settler is a simple migration framework for Flask, SQLAlchemy, and Flask-SQLAlchmey.

```python
from flask_sqlalchemy import SQLAlchemy
from settler import MigrationManager


my_db = SQLAlchemy({ ... })

migration_manager = MigrationManager(my_db, migrations_dir='migrations')

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
