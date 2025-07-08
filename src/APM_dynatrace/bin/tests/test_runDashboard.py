import unittest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from runDashboard import main

class TestRunDashboard(unittest.TestCase):

    @patch.dict(os.environ, {'DTUSER': 'testuser', 'DTPASS': 'testpass'})
    @patch('runDashboard.build_opener')
    @patch('runDashboard.ET.parse')
    @patch('runDashboard.ET.XSLT')
    def test_run_dashboard_success(self, mock_xslt, mock_et_parse, mock_build_opener):
        # Arrange
        mock_opener = MagicMock()
        mock_build_opener.return_value = mock_opener
        mock_et_parse.side_effect = [MagicMock(), MagicMock()] # First for XML, second for XSL
        mock_transform = MagicMock()
        mock_xslt.return_value = mock_transform
        mock_transform.return_value = "<transformed>output</transformed>"

        # Act
        with patch('sys.argv', ['runDashboard.py', '--dtserver', 'localhost:8020', '--dashboard', 'TestDashboard']):
            with patch('builtins.print') as mock_print:
                main()

        # Assert
        mock_build_opener.assert_called_once()
        self.assertEqual(mock_et_parse.call_count, 2)
        mock_xslt.assert_called_once()
        mock_transform.assert_called_once()
        mock_print.assert_called_with('<transformed>output</transformed>')

    @patch.dict(os.environ, {}, clear=True)
    def test_run_dashboard_no_creds(self):
        # Act & Assert
        with patch('sys.argv', ['runDashboard.py']):
            with self.assertRaises(SystemExit) as cm:
                with patch('builtins.print') as mock_print:
                    main()
            self.assertEqual(cm.exception.code, 1)
            mock_print.assert_called_with("Error: DTUSER and DTPASS environment variables must be set.", file=sys.stderr)

if __name__ == '__main__':
    unittest.main()
