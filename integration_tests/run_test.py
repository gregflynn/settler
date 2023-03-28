import subprocess
import traceback
from functools import wraps

from sqlalchemy import create_engine
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


def get_db_url():
    info = {
        'db_user': 'settler',
        'db_pass': 'settlertest',
        'db_name': 'settler',
        'db_host': 'localhost',
        'db_port': '5432'
    }
    return ("postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
            .format(**info))


def flask_sql_engine():
    flask_app = Flask(__name__)
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = get_db_url()
    with flask_app.app_context():
        return SQLAlchemy(flask_app).engine


def sql_engine():
    return create_engine(get_db_url(), client_encoding='utf8')


ENGINES = {
    'SQLAlchemy Engine': sql_engine,
    'Flask-SQLAlchemy Engine': flask_sql_engine
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


def assertDatabaseRevision(mgr, revision):
    """ make an assertion that the database is a particular version
    """
    assert mgr.status.get_current_migration() == revision


def assertDirectoryRevision(mgr, revision):
    """ make an assertion that the migrations directory is a particular version
    """
    assert mgr.migs.highest_revision == revision


def test(test_func):
    @wraps(test_func)
    def wrapper():
        for mig_dir, name, engine_builder in test_generator():
            test_name = '{} on {} in {}'.format(test_func.__name__,
                                                name, mig_dir)
            print(MSG.format(t='Running', msg=test_name))

            subprocess.call('./create_db.sh')
            engine = engine_builder()

            try:
                test_func(engine, mig_dir, MIGRATIONS[mig_dir])
            except Exception as e:
                print(MSG.format(t='Error', msg=e))
                ERROR_TESTS.append(test_name)
                traceback.print_exc()
            finally:
                engine.dispose()
                subprocess.call('./drop_db.sh')
                print(MSG.format(t='Finished', msg=test_name))
                print(BAR)

    REGISTERED_TESTS.append(wrapper)
    return wrapper


@test
def main_test(engine, migrations_dir, expectations):
    with MigrationManager(engine, migrations_dir=migrations_dir) as mgr:
        assertDirectoryRevision(mgr, expectations['directory_version'])
        assertDatabaseRevision(mgr, -1)
        mgr.check()

        mgr.update()
        mgr.check()
        assertDatabaseRevision(mgr, expectations['after_1st_update'])

        mgr.undo()
        mgr.check()
        assertDatabaseRevision(mgr, expectations['after_1st_undo'])

        mgr.undo()
        mgr.check()
        assertDatabaseRevision(mgr, expectations['after_2nd_undo'])

        mgr.update()
        mgr.check()
        assertDatabaseRevision(mgr, expectations['after_2nd_update'])


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
