from os import listdir

from .files import MigrationFile
from .models import DatabaseStatus


CHECK_MSG = '''
  Database Revision: {db_rev}
Migrations Revision: {mig_rev}'''
UPDATE_MSG = 'Up to date!'
UNDO_MSG = 'Already at oldest revision'


class MigrationManager(object):
    def __init__(self, engine, migrations_dir='migrations'):
        """
        Args:
            engine: database engine for migration management
            migrations_dir (str): path to migrations files
        """
        if migrations_dir[-1] == '/':
            migrations_dir = migrations_dir[0:-1]

        from sqlalchemy.orm import sessionmaker
        self.session = sessionmaker(bind=engine)()
        self.status = DatabaseStatus(self.session, engine)
        self.dir = migrations_dir

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.session:
            self.session.close()

    def check(self):
        """ Print the current revision of the database and newest revision
        available in the migrations directory
        """
        rev = self.status.get_current_migration()
        migrations = self._read_migrations()
        print(CHECK_MSG.format(
            db_rev=rev if rev >= 0 else None,
            mig_rev=migrations[-1].rev if migrations else None))

    def update(self):
        """ Migrate the database to the most up to date revision
        """
        rev = self.status.get_current_migration()
        migrations = self._read_migrations()
        for migration in migrations[rev+1:]:
            self._run(migration)
        print(UPDATE_MSG)

    def undo(self):
        """ Reverts the current revision
        """
        rev = self.status.get_current_migration()

        if rev == DatabaseStatus.NO_REVISION:
            print(UNDO_MSG)
            return

        migrations = self._read_migrations()
        self._run(migrations[rev], undo=True)

    def _run(self, migration, undo=False):
        print('Running migration: {filename}\n{sql}'.format(
            filename=migration.filename,
            sql=migration.get_sql(undo=undo))
        )
        sql = migration.undo if undo else migration.do
        self.session.execute(sql)
        self.status.set_current_migration(migration.rev
                                          if not undo else migration.rev - 1)

    def _read_migrations(self):
        """ private: read all migrations from disk, validate, and sort
        """
        migrations = [MigrationFile('{}/{}'.format(self.dir, p))
                      for p in listdir(self.dir)]
        migrations.sort(key=lambda m: m.rev)
        self._validate_migrations(migrations)
        return migrations

    def _validate_migrations(self, migrations):
        """ private: validate the migration set as a whole exception if invalid
        """
        for i, m in zip(range(0, len(migrations)), migrations):
            if i != m.rev:
                raise Exception()
