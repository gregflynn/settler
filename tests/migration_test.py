from unittest import TestCase
from unittest.mock import patch, mock_open

from settler.migration import Migration


class MigrationTests(TestCase):
    @patch('builtins.open', mock_open(read_data='a line\nanother line'))
    def test_read_file(self):
        expected = 'a line\n another line'
        result = Migration._read_file('some path')
        self.assertEqual(expected, result)

    def another_test(self):
        pass
