import re
from os import listdir
from os.path import basename


class MigrationDirectory(object):
    NO_REVISION = -1
    NEW_TEMPLATE = '-- @DO\n\n\n-- @UNDO\n'

    def __init__(self, migration_dir):
        self.dir = migration_dir
        self._read()

    def _read(self):
        migrations = [MigrationFile('{}/{}'.format(self.dir, p))
                      for p in listdir(self.dir)]
        migrations.sort(key=lambda m: m.rev)
        self._validate(migrations)
        self.migrations = migrations

    @staticmethod
    def _validate(migrations):
        """ private: validate the migration set as a whole exception if invalid
        """
        for i, m in zip(range(0, len(migrations)), migrations):
            if i != m.rev:
                raise NonContiguousMigrationsException()

    @property
    def length(self):
        return len(self.migrations)

    @property
    def highest_revision(self):
        return self.length - 1 if self.length > 0 else self.NO_REVISION

    def __getitem__(self, revision):
        return self.migrations[revision]

    def new(self, name):
        """ Create a new migration with the given name

        Args:
            name (str): name to give the new migration
        """
        revision = self.highest_revision + 1
        filename = '{}/{:03d}_{}.sql'.format(self.dir, revision, name)
        with open(filename, 'w') as f:
            f.write(self.NEW_TEMPLATE)
        return filename


class MigrationFile(object):
    COMMENTS_REGEX = re.compile('--.*?$', re.M)

    def __init__(self, path):
        """
        Args:
            path (str): path to the migration file
        """
        self._path = path
        self._filename = basename(path)
        self._raw = self._read_file(path)
        self._rev = self._parse_rev(self._filename)
        self._do, self._undo = self._parse_sql(self._filename, self._raw)

    @property
    def filename(self):
        return self._filename

    @property
    def path(self):
        return self._path

    @property
    def rev(self):
        """ integer revision of this migration
        """
        return self._rev

    @property
    def do(self):
        """ sql string for performing this migration
        """
        return self._do

    @property
    def undo(self):
        """ sql string for reverting this migration
        """
        return self._undo

    def get_sql(self, undo=False):
        """ Convenience method wrapping do/undo with a boolean

        Args:
            undo (boolean:False): Specify True to get undo sql

        Returns:
            (str) sql
        """
        return self.undo if undo else self.do

    @staticmethod
    def _read_file(path):
        """ Read the migration file

        Args:
            path (str): path to the migration file we're reading

        Returns:
            str contents of the file
        """
        with open(path, 'r') as f:
            raw = ' '.join(f.readlines())
        return raw  # https://media.giphy.com/media/PjJw7ql19k0AU/giphy.gif

    @staticmethod
    def _parse_rev(filename):
        """ Parse out the revision number from the given filename

        Args:
            filename (str): filename to parse revision from

        Returns:
            int revision number
        """
        try:
            rev = int(filename.split('_', 1)[0])
        except:
            raise RevisionUnparsableException(filename)
        if rev < 0:
            raise RevisionTooLowException(filename)
        return rev

    @classmethod
    def _parse_sql(cls, filename, raw):
        """ Parse the migration file into do/undo statements

        Args:
            raw (str): contents of the migration file

        Returns:
            (str, str) do and undo sql respectively
        """
        try:
            raw_do, raw_undo = raw.split('@UNDO')
        except ValueError:
            raise UnseparableException(filename)

        return cls._strip(raw_do), cls._strip(raw_undo)

    @classmethod
    def _strip(cls, sql):
        """ Remove comments and extra whitespace from sql

        Args:
            sql (str): sql string needing stripping

        Returns:
            (str) sql stripped of comments and whitespace
        """
        return cls.COMMENTS_REGEX.sub('', sql).strip()


class RevisionUnparsableException(Exception):
    """ Failed to parse the revision number out of the file name
    """


class UnseparableException(Exception):
    """ Means the migration could not be split into DO and UNDO correctly
    """


class RevisionTooLowException(Exception):
    """ The revision number parsed from the filename was less than zero
    """


class NonContiguousMigrationsException(Exception):
    """ Migration revision numbers do not increment by 1 from 0
    """
