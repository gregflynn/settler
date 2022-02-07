from sqlalchemy import Column, Integer, inspect
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class MigrationStatus(Base):
    __tablename__ = 'migration'

    # NOTE: primary_key just so sqlalchemy doesn't yell at me, autoincrement off so
    #       mysql/mariadb don't change the value when we insert it
    revision = Column(Integer, primary_key=True, autoincrement=False)

    def __init__(self, revision):
        self.revision = revision


class DatabaseStatus(object):
    NO_REVISION = -1

    def __init__(self, session, engine):
        self.engine = engine
        self.session = session

    def _current(self):
        insp = inspect(self.engine)
        if not insp.has_table(MigrationStatus.__tablename__):
            MigrationStatus.__table__.create(bind=self.engine)
        return self.session.query(MigrationStatus).first()

    def get_current_migration(self):
        """ Get the database's current migration revision

        Returns:
            integer revision of the database or -1 if database reflects no
            migrations applied
        """
        status = self._current()
        return self.NO_REVISION if status is None else status.revision

    def set_current_migration(self, new_revision):
        """ Set the database's current revision

        Args:
            new_revision (int): the new revision number to set

        Returns:
            the migration revision that was just set
        """
        row = self._current()

        if row is None:
            row = MigrationStatus(new_revision)
        else:
            row.revision = new_revision

        self.session.add(row)
        self.session.commit()
        print('At revision {}'.format(row.revision))
        return row.revision
