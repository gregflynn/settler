import re
from os.path import basename


REMOVE_COMMENTS_RE = re.compile('--.*?\n')
SQL_TOO_SHORT_THRESHOLD = 5


class Migration(object):
    def __init__(self, path):
        """
        Args:
            path (str): path to the migration file
        """
        self._path = path
        self._filename = basename(path)
        self._raw = self._read_file(path)
        self._rev = self._parse_rev(self._filename)
        self._do, self._undo = self._parse_sql(self._raw)

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

    def _read_file(self, path):
        """ Read the migration file

        Args:
            path (str): path to the migration file we're reading

        Returns:
            str contents of the file
        """
        with open(path, 'r') as f:
            raw = ' '.join(f.readlines())
        return raw  # https://media.giphy.com/media/PjJw7ql19k0AU/giphy.gif

    def _parse_rev(self, filename):
        """ Parse out the revision number from the given filename

        Args:
            filename (str): filename to parse revision from

        Returns:
            int revision number
        """
        try:
            rev = int(filename.split('_', 1)[0])
        except:
            raise Exception(
                'Bad Migration: revision unparseable in {}'.format(filename))
        if rev < 0:
            raise Exception(
                'Bad Migration: revision < 0 in {}'.format(filename))
        return rev

    def _parse_sql(self, filename, raw):
        """ Parse the migration file into do/undo statements

        Args:
            raw (str): contents of the migration file

        Returns:
            (str, str) do and undo sql respectively
        """
        try:
            raw_do, raw_undo = raw.split('@UNDO')
        except ValueError:
            raise Exception(
                'Bad Migration: failed to separate do/undo in {}'.format(
                    self._filename))

        do = self._strip_comments(raw_do)
        undo = self._strip_comments(raw_undo)
        return do, undo

    def _strip_comments(self, sql):
        """ Remove comments from sql

        Args:
            sql (str): sql string needing stripping

        Returns:
            (str) sql stripped of comments
        """
        return re.sub(REMOVE_COMMENTS_RE, '', sql)
