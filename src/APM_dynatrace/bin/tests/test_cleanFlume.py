import unittest
import os
import datetime
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cleanFlume import main

class TestCleanFlume(unittest.TestCase):

    @patch('os.walk')
    @patch('os.path.getmtime')
    @patch('os.remove')
    @patch('os.path.dirname')
    @patch('os.chdir')
    def test_clean_flume(self, mock_chdir, mock_dirname, mock_remove, mock_getmtime, mock_walk):
        # Arrange
        mock_dirname.return_value = '/fake/dir'
        mock_walk.return_value = [
            ('/fake/dir/log', ('subdir',), ('file1.log', 'file2.log')),
            ('/fake/dir/log/subdir', (), ('file3.log',))
        ]

        # Mock file modification times
        now = datetime.datetime.now()
        old_time = (now - datetime.timedelta(hours=25)).timestamp()
        new_time = (now - datetime.timedelta(hours=1)).timestamp()
        mock_getmtime.side_effect = [old_time, new_time, old_time]

        # Act
        with patch('builtins.print') as mock_print:
            main()

        # Assert
        self.assertEqual(mock_remove.call_count, 2)
        mock_remove.assert_any_call('/fake/dir/log/file1.log')
        mock_remove.assert_any_call('/fake/dir/log/subdir/file3.log')
        mock_print.assert_any_call("App directory:", '/fake/dir', file=sys.stderr)
        mock_chdir.assert_called_once_with('/fake/dir')

if __name__ == '__main__':
    unittest.main()
