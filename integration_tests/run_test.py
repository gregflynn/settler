import subprocess
import traceback
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from settler import MigrationManager


REGISTERED_TESTS = []
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
    return SQLAlchemy(flask_app).engine


def sql_engine():
    return create_engine(get_db_url(), client_encoding='utf8')


ENGINES = {
    'SQLAlchemy Engine': sql_engine,
    'Flask-SQLAlchemy Engine': flask_sql_engine
}

MIGRATIONS = ['migrations_1', 'migrations_2']


def test(test_func):
    @wraps(test_func)
    def wrapper():
        for mig_dir in MIGRATIONS:
            for name, engine_builder in ENGINES.items():
                test_name = '{} on {} in {}'.format(test_func.__name__,
                                                    name, mig_dir)
                print(MSG.format(t='Running', msg=test_name))

                subprocess.call('./create_db.sh')
                engine = engine_builder()
                session = sessionmaker(bind=engine)()

                try:
                    test_func(engine, session, mig_dir)
                except Exception as e:
                    print(MSG.format(t='Error', msg=e))
                    traceback.print_exc()
                finally:
                    session.close()
                    engine.dispose()
                    subprocess.call('./drop_db.sh')
                    print(MSG.format(t='Finished', msg=test_name))
                    print(BAR)

    REGISTERED_TESTS.append(wrapper)
    return wrapper


@test
def main_test(engine, session, migrations_dir):
    manager = MigrationManager(engine,
                               session=session,
                               migrations_dir=migrations_dir)
    manager.check()
    manager.update()
    manager.check()


# run all the tests!
for test in REGISTERED_TESTS:
    test()
