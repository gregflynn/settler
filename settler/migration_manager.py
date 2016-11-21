from os import listdir
from typing import Iterable

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import ProgrammingError

from .migration import Migration


class MigrationManager(object):
    db = None

    def __init__(self, db: SQLAlchemy, migrations_dir: str='migrations'):
        if migrations_dir[-1] == '/':
            migrations_dir = migrations_dir[0:-1]
        self.db = db
        self.dir = migrations_dir
        self._build_migration_table(db)

    def check(self) -> None:
        """ Print the current revision of the database and newest revision
        available in the migrations directory
        """
        rev = self._get_revision()
        migrations = self._read_migrations()
        print('''
          Database Revision: {db_rev}
        Migrations Revision: {mig_rev}
        '''.format(db_rev=rev if rev >= 0 else None,
                   mig_rev=migrations[-1].rev if migrations else None))

    def update(self) -> None:
        """ Migrate the database to the most up to date revision
        """
        rev = self._get_revision()
        migrations = self._read_migrations()
        for migration in migrations[rev+1:]:
            self._run(migration)
        print('Up to date!')

    def undo(self) -> None:
        """ Reverts the current revision
        """
        rev = self._get_revision()
        migrations = self._read_migrations()
        self._run(migrations[rev], undo=True)

    def _run(self, migration, undo=False):
        print('Running migration: {filename}\n{sql}'.format(
            filename=migration.filename,
            sql=migration.get_sql(undo=undo))
        )
        sql = migration.undo if undo else migration.do
        self.db.engine.execute(sql)
        self._set_migration(migration.rev if not undo else migration.rev - 1)

    def _get_revision(self) -> int:
        """ private: get the current revision number
        """
        try:
            return self.MigrationTable.query.first().revision
        except ProgrammingError:
            self.MigrationTable.__table__.create(bind=self.db.engine)
            return -1
        except AttributeError:
            return -1

    def _set_migration(self, new_revision: int) -> None:
        """ private: set the migration number in the database
        """
        table = self.MigrationTable.query.first()
        if table is None:
            table = self.MigrationTable(new_revision)
        else:
            table.revision = new_revision
        self.db.session.add(table)
        self.db.session.commit()
        print('At revision {}'.format(new_revision))

    def _read_migrations(self) -> Iterable[Migration]:
        """ private: read all migrations from disk, validate, and sort
        """
        migrations = [Migration('{}/{}'.format(self.dir, p))
                      for p in listdir(self.dir)]
        migrations.sort(key=lambda m: m.rev)
        self._validate_migrations(migrations)
        return migrations

    def _validate_migrations(self, migrations: Iterable[Migration]) -> None:
        """ private: validate the migration set as a whole exception if invalid
        """
        for i, m in zip(range(0, len(migrations)), migrations):
            if i != m.rev:
                raise Exception()

    def _build_migration_table(self, db: SQLAlchemy) -> None:
        """ private: build the model for the migration table
        """
        class MigrationTable(db.Model):
            __tablename__ = 'migration'
            revision = db.Column(db.Integer, primary_key=True)

            def __init__(self, revision: int):
                self.revision = revision
        self.MigrationTable = MigrationTable
