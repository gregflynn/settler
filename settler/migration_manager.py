from .files import MigrationDirectory
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
        self.migs = MigrationDirectory(migrations_dir)

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
        mig_rev = self.migs.highest_revision
        print(CHECK_MSG.format(
            db_rev=rev if rev >= 0 else None,
            mig_rev=mig_rev if mig_rev >= 0 else None))

    def update(self):
        """ Migrate the database to the most up to date revision
        """
        [self._run(x) for x in range(self.status.get_current_migration() + 1,
                                     self.migs.highest_revision + 1)]
        print(UPDATE_MSG)

    def undo(self):
        """ Reverts the current revision
        """
        rev = self.status.get_current_migration()

        if rev == DatabaseStatus.NO_REVISION:
            print(UNDO_MSG)
            return

        self._run(rev, undo=True)

    def new(self, name):
        """ Create a new migration of the given name

        Args:
            name (str): name to give to the migration
        """
        filename = self.migs.new(name)
        print('Created {}'.format(filename))

    def _run(self, revision, undo=False):
        migration = self.migs[revision]
        sql = migration.get_sql(undo=undo)
        print('Running migration: {filename}\n{sql}'.format(
            filename=migration.filename, sql=sql))
        self.session.execute(sql)
        self.status.set_current_migration(migration.rev
                                          if not undo else migration.rev - 1)
