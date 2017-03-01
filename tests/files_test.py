from unittest import TestCase
from unittest.mock import patch, mock_open

from settler.files import (MigrationFile, RevisionTooLowException,
                           RevisionUnparsableException)


class MigrationFileTests(TestCase):
    @patch('builtins.open', mock_open(read_data='a line\nanother line'))
    def test_read_file(self):
        expected = 'a line\n another line'
        result = MigrationFile._read_file('some path')
        self.assertEqual(expected, result)

    def test_parse_revision(self):
        self.assertEqual(1, MigrationFile._parse_rev('001_foo.sql'))
        self.assertEqual(1, MigrationFile._parse_rev('001____f____o___o.sql'))
        with self.assertRaises(RevisionUnparsableException):
            MigrationFile._parse_rev('foo.sql')

        with self.assertRaises(RevisionTooLowException):
            MigrationFile._parse_rev('-1_foo.sql')

    def test_parse_sql_good(self):
        raw = '''-- @DO
        create table
        -- @UNDO
        drop table
        '''
        do, undo = MigrationFile._parse_sql('filename', raw)
        self.assertEqual(do, 'create table')
        self.assertEqual(undo, 'drop table')

    def test_strip_comments_end_of_line(self):
        raw = 'create table -- comment at end of line!'
        expected = 'create table'
        actual = MigrationFile._strip(raw)
        self.assertEqual(expected, actual)

    def test_strip_comments_whole_line(self):
        raw = '''
        create table
        -- comment on another line!
        '''
        expected = 'create table'
        actual = MigrationFile._strip(raw)
        self.assertEqual(expected, actual)

    def test_strip_comments_multiple_whole_line(self):
        raw = '''
        -- comment
        create table
        -- a comment
        -- comment on another line!'''
        expected = 'create table'
        actual = MigrationFile._strip(raw)
        self.assertEqual(expected, actual)
