import re
from os.path import basename


class Migration(object):
    def __init__(self, filename: str):
        self._parse_filename(filename)
        self._parse_file(filename)

    @property
    def filename(self):
        return self._filename

    @property
    def rev(self):
        return self._rev

    @property
    def do(self):
        return self._do

    @property
    def undo(self):
        return self._undo

    def get_sql(self, undo: bool=False) -> str:
        """
        """
        return self.undo if undo else self.do

    _remove_comments_re = re.compile('--.*?\n')

    def _parse_filename(self, filename: str):
        self._filename = filename
        name = basename(filename)
        try:
            self._rev = int(name.split('_', 1)[0])
        except:
            raise Exception('''Malformed migration: could not parse revision
                            for {}'''.format(filename))
        if self._rev < 0:
            raise Exception('Malformed migration: revision less than zero {}'
                            .format(filename))

    def _parse_file(self, filename: str):
        raw = ' '.join(open(filename, 'r').readlines())
        split = raw.split('@UNDO')

        if len(split) != 2:
            raise Exception('''Malformed migration: do/undo could not be split
                            for {}'''.format(filename))
        self._do = self._strip_comments(split[0]).strip()
        self._undo = self._strip_comments(split[1]).strip()
        if len(self._do) < 5:
            # this is stupid short
            raise Exception('Malformed migration: @DO is too short in {}'
                            .format(filename))
        if len(self._undo) < 5:
            # this is stupid short
            raise Exception('Malformed migration: @UNDO is too short in {}'
                            .format(filename))

    def _strip_comments(self, sql: str) -> str:
        return re.sub(self._remove_comments_re, '', sql)
