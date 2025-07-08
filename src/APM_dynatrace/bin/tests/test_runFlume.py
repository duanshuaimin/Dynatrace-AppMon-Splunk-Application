import unittest
import os
import sys
import subprocess
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from runFlume import main, check_java_version

class TestRunFlume(unittest.TestCase):

    @patch('subprocess.call')
    def test_check_java_version_success(self, mock_call):
        mock_call.return_value = 0
        with patch('builtins.print') as mock_print:
            check_java_version()
        mock_print.assert_called_with("Java version check successful.")

    @patch('subprocess.call', side_effect=OSError("Command not found"))
    def test_check_java_version_fail(self, mock_call):
        with self.assertRaises(SystemExit) as cm:
            with patch('builtins.print') as mock_print:
                check_java_version()
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(mock_print.call_args[0][0], "Execution failed:")

    @patch('runFlume.check_java_version')
    @patch('subprocess.Popen')
    @patch('os.path.exists', return_value=False)
    @patch('os.name', 'posix')
    @patch('os.path.dirname')
    @patch('os.chdir')
    def test_run_flume_posix_no_pid_file(self, mock_chdir, mock_dirname, mock_exists, mock_popen, mock_check_java):
        # Arrange
        mock_dirname.return_value = '/fake/app'
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'stdout', b'stderr')
        mock_process.wait.return_value = 0
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        # Act
        with patch('builtins.open', mock_open()) as m:
            with patch('builtins.print') as mock_print:
                main()

        # Assert
        mock_popen.assert_called_once()
        m.assert_called_with(os.path.join('/fake/app', 'flume.pid'), 'w')
        m().write.assert_called_with('12345')
        mock_print.assert_any_call(b'stdout'.decode())
        mock_print.assert_any_call(b'stderr'.decode(), file=sys.stderr)

    @patch('runFlume.check_java_version')
    @patch('subprocess.check_output')
    @patch('os.path.exists', return_value=False)
    @patch('os.name', 'nt')
    @patch('os.path.dirname')
    @patch('os.chdir')
    def test_run_flume_nt_no_pid_file(self, mock_chdir, mock_dirname, mock_exists, mock_check_output, mock_check_java):
        # Arrange
        mock_dirname.return_value = '/fake/app'
        mock_check_output.side_effect = subprocess.CalledProcessError(1, 'cmd') # Simulate process not found

        # Act & Assert
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b'', b'')
            mock_process.wait.return_value = 0
            mock_process.pid = 56789
            mock_popen.return_value = mock_process
            with patch('builtins.open', mock_open()) as m:
                main()
                mock_popen.assert_called_once()
                m.assert_called_with(os.path.join('/fake/app', 'flume.pid'), 'w')
                m().write.assert_called_with('56789')

if __name__ == '__main__':
    unittest.main()
