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

with MigrationManager(engine, migrations_dir='migrations') as mgr:

    """ Check the database and migrations folder highest versions and print them
    """
    mgr.check()

    """ Bring your db up to the highest revision from the migrations folder
    """
    mgr.update()

    """ Undo the last migration applied
    """
    mgr.undo()

    """ Make a new migration
    """
    mgr.new('new_migration')
    # creates `migrations/000_new_migration.sql`
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


## Development

### Dependencies
- Create a virtualenv for settler
    - `pyenv virtualenv 3.10.9 settler`
- Activate that virtualenv on `cd`
    - `pyenv local settler`
- Install runtime and test requirements
    - `pip install -e . -r test_requirements.txt`

### Running Tests
#### Unit Tests
- `pytest tests`

#### Integration Tests
- Stand up docker compose
- `cd integration_tests`
- `python run_test.py`
