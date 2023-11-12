import subprocess
import traceback
from functools import wraps

import click
from sqlalchemy import create_engine, text
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from settler import MigrationManager
from settler.models import DatabaseStatus


REGISTERED_TESTS = []
ERROR_TESTS = []
BAR = '''
===============================================================================
'''
MSG = '=== {t}: {msg}'

POSTGRES_DB_URL = "postgresql://settler:settlertest@localhost:5432/settler"
MARIADB_ROOT_URL = "mariadb+mariadbconnector://root:rootpw@127.0.0.1:3306"


def flask_sql_engine():
    flask_app = Flask(__name__)
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_DB_URL
    with flask_app.app_context():
        return SQLAlchemy(flask_app).engine


def postgres_sql_engine():
    return create_engine(POSTGRES_DB_URL, client_encoding='utf8')


def maria_sql_engine():
    return create_engine(
        "mariadb+mariadbconnector://settler:settlerpassword@127.0.0.1:3306/settlerdb",
        future=True,
        pool_recycle=600,
    )


ENGINES = {
    'SQLAlchemy Engine (psql)': postgres_sql_engine,
    'Flask-SQLAlchemy Engine': flask_sql_engine,
    'SQLAlchemy Engine (mariadb)': maria_sql_engine,
}

MIGRATIONS = {
    'migrations_1': {
        'directory_version': 0,
        'after_1st_update': 0,
        'after_1st_undo': DatabaseStatus.NO_REVISION,
        'after_2nd_undo': DatabaseStatus.NO_REVISION,
        'after_2nd_update': 0
    },
    'migrations_2': {
        'directory_version': DatabaseStatus.NO_REVISION,
        'after_1st_update': DatabaseStatus.NO_REVISION,
        'after_1st_undo': DatabaseStatus.NO_REVISION,
        'after_2nd_undo': DatabaseStatus.NO_REVISION,
        'after_2nd_update': DatabaseStatus.NO_REVISION
    },
    'migrations_3': {
        'directory_version': 2,
        'after_1st_update': 2,
        'after_1st_undo': 1,
        'after_2nd_undo': 0,
        'after_2nd_update': 2
    }
}


def test_generator():
    for mig_dir in MIGRATIONS.keys():
        for name, engine_builder in ENGINES.items():
            yield mig_dir, name, engine_builder


def assert_database_revision(mgr, revision):
    """ make an assertion that the database is a particular version
    """
    assert mgr.status.get_current_migration() == revision


def assert_directory_revision(mgr, revision):
    """ make an assertion that the migrations directory is a particular version
    """
    assert mgr.migs.highest_revision == revision


def create_db(db_type):
    if db_type == "psql":
        subprocess.call("scripts/create_psql_db.sh")
    else:
        engine = create_engine(MARIADB_ROOT_URL)
        connection = engine.connect()

        connection.execute(text("CREATE DATABASE IF NOT EXISTS settlerdb"))
        connection.execute(text("GRANT ALL PRIVILEGES ON settlerdb.* TO settler"))


def drop_db(db_type):
    if db_type == "psql":
        subprocess.call("scripts/drop_psql_db.sh")
    else:
        engine = create_engine(MARIADB_ROOT_URL)
        connection = engine.connect()

        connection.execute(text("DROP DATABASE IF EXISTS settlerdb"))


def test(test_func):
    @wraps(test_func)
    def wrapper():
        for mig_dir, name, engine_builder in test_generator():
            test_name = f"{test_func.__name__} on {name} in {mig_dir}"
            click.secho(MSG.format(t='Running', msg=test_name), fg="yellow")

            db_type = "mariadb" if "mariadb" in name else "psql"
            create_db(db_type)

            engine = engine_builder()

            try:
                test_func(engine, mig_dir, MIGRATIONS[mig_dir])
            except Exception as e:
                click.secho(MSG.format(t="Error", msg=e), fg="red")
                ERROR_TESTS.append(test_name)
                traceback.print_exc()
            finally:
                engine.dispose()
                drop_db(db_type)
                click.secho(MSG.format(t='Finished', msg=test_name), fg="yellow")
                print(BAR)

    REGISTERED_TESTS.append(wrapper)
    return wrapper


@test
def main_test(engine, migrations_dir, expectations):
    with MigrationManager(engine, migrations_dir=migrations_dir) as mgr:
        assert_directory_revision(mgr, expectations['directory_version'])
        assert_database_revision(mgr, DatabaseStatus.NO_REVISION)
        mgr.check()

        mgr.update()
        mgr.check()
        assert_database_revision(mgr, expectations['after_1st_update'])

        mgr.undo()
        mgr.check()
        assert_database_revision(mgr, expectations['after_1st_undo'])

        mgr.undo()
        mgr.check()
        assert_database_revision(mgr, expectations['after_2nd_undo'])

        mgr.update()
        mgr.check()
        assert_database_revision(mgr, expectations['after_2nd_update'])


# run all the tests!
for test in REGISTERED_TESTS:
    test()

if ERROR_TESTS:
    print('''
    FAILURE ({})
    '''.format(len(ERROR_TESTS)))
    for er_test in ERROR_TESTS:
        print(er_test)
else:
    print('''
    SUCCESS!
    ''')
