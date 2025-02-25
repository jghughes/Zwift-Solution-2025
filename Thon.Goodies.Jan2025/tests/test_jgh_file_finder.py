import unittest
import os
from unittest.mock import patch, mock_open, MagicMock
from jgh_file_finder import find_directory_that_contains_file

class TestSearchForPathToFile(unittest.TestCase):

    def setUp(self):
        # Set the BASE_DIR environment variable for testing
        os.environ['BASE_DIR'] = '/mocked/path'

    def tearDown(self):
        # Clean up the BASE_DIR environment variable after testing
        del os.environ['BASE_DIR']

    @patch('os.walk')
    def test_find_directory_with_valid_file(self, mock_walk: MagicMock) -> None:
        mock_walk.return_value = [
            ('/mocked/path', ('subdir',), ('appsettings.json',)),
            ('/mocked/path/subdir', (), ()),
        ]

        dir_path = find_directory_that_contains_file('appsettings.json')
        self.assertEqual(dir_path, '/mocked/path')

    @patch('os.walk')
    def test_find_directory_with_file_in_subdirectory(self, mock_walk: MagicMock) -> None:
        mock_walk.return_value = [
            ('/mocked/path', ('subdir',), ()),
            ('/mocked/path/subdir', (), ('appsettings.json',)),
        ]

        dir_path = find_directory_that_contains_file('appsettings.json')
        self.assertEqual(dir_path, '/mocked/path/subdir')

    @patch('os.walk')
    def test_find_directory_with_nonexistent_file(self, mock_walk: MagicMock) -> None:
        mock_walk.return_value = [
            ('/mocked/path', ('subdir',), ()),
            ('/mocked/path/subdir', (), ()),
        ]

        dir_path = find_directory_that_contains_file('appsettings.json')
        self.assertIsNone(dir_path)

    @patch('os.getcwd')
    @patch('os.walk')
    def test_find_directory_with_no_parent_dir_provided(self, mock_walk: MagicMock, mock_getcwd: MagicMock) -> None:
        mock_getcwd.return_value = '/mocked/current/dir'
        mock_walk.return_value = [
            ('/mocked/current/dir', ('subdir',), ('appsettings.json',)),
            ('/mocked/current/dir/subdir', (), ()),
        ]

        dir_path = find_directory_that_contains_file('appsettings.json')
        self.assertEqual(dir_path, '/mocked/current/dir')

    @patch('os.walk')
    def test_find_directory_with_invalid_parent_dir(self, mock_walk: MagicMock) -> None:
        dir_path = find_directory_that_contains_file('appsettings.json', '/invalid/path')
        self.assertIsNone(dir_path)

if __name__ == '__main__':
    unittest.main(verbosity=2)
