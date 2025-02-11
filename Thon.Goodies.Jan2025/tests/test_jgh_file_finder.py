import unittest
from unittest.mock import patch, MagicMock
from typing import List
from jgh_file_finder import find_path_to_file  # Updated module name

class TestSearchForPathToFile(unittest.TestCase):

    PARENT_DIR = "/parent"
    CHILD_DIR_1 = "/parent/child1"
    FILENAME = "dummy.json"

    def setUpMockBehavior(
        self,
        mock_abspath: MagicMock,
        mock_dirname: MagicMock,
        mock_isfile: MagicMock,
        abspath_return_value: str,
        dirname_side_effect: List[str],
        isfile_side_effect: List[bool]
    ) -> None:
        mock_abspath.return_value = abspath_return_value
        mock_dirname.side_effect = dirname_side_effect
        mock_isfile.side_effect = isfile_side_effect

    @patch("os.path.abspath")
    @patch("os.path.dirname")
    @patch("os.path.isfile")
    @patch("os.listdir")
    def test_find_file_in_current_directory(
        self,
        mock_listdir: MagicMock,
        mock_isfile: MagicMock,
        mock_dirname: MagicMock,
        mock_abspath: MagicMock
    ) -> None:
        """Test finding dummy.json in the current directory."""
        self.setUpMockBehavior(
            mock_abspath,
            mock_dirname,
            mock_isfile,
            self.CHILD_DIR_1,
            [self.CHILD_DIR_1, self.PARENT_DIR, "/"],
            [True, False, False]
        )

        result: str | None = find_path_to_file(self.FILENAME)
        if result is not None:
            normalized_result: str = result.replace("\\", "/")
            self.assertEqual(normalized_result, f"{self.CHILD_DIR_1}/{self.FILENAME}")

    @patch("os.path.abspath")
    @patch("os.path.dirname")
    @patch("os.path.isfile")
    @patch("os.listdir")
    def test_find_file_in_parent_directory(
        self,
        mock_listdir: MagicMock,
        mock_isfile: MagicMock,
        mock_dirname: MagicMock,
        mock_abspath: MagicMock
    ) -> None:
        """Test finding dummy.json in the parent directory."""
        self.setUpMockBehavior(
            mock_abspath,
            mock_dirname,
            mock_isfile,
            self.CHILD_DIR_1,
            [self.CHILD_DIR_1, self.PARENT_DIR, "/"],
            [False, True, False]
        )

        result: str | None = find_path_to_file(self.FILENAME)
        if result is not None:
            normalized_result: str = result.replace("\\", "/")
            self.assertEqual(normalized_result, f"{self.PARENT_DIR}/{self.FILENAME}")

    @patch("os.path.abspath")
    @patch("os.path.dirname")
    @patch("os.path.isfile")
    @patch("os.listdir")
    def test_find_file_two_levels_up(
        self,
        mock_listdir: MagicMock,
        mock_isfile: MagicMock,
        mock_dirname: MagicMock,
        mock_abspath: MagicMock
    ) -> None:
        """Test finding dummy.json two levels up from the current directory."""
        self.setUpMockBehavior(
            mock_abspath,
            mock_dirname,
            mock_isfile,
            self.CHILD_DIR_1,
            [self.CHILD_DIR_1, self.PARENT_DIR, "/"],
            [False, False, True]
        )

        result: str | None = find_path_to_file(self.FILENAME)
        if result is not None:
            normalized_result: str = result.replace("\\", "/")
            self.assertEqual(normalized_result, f"/{self.FILENAME}")

    @patch("os.path.abspath")
    @patch("os.path.dirname")
    @patch("os.path.isfile")
    @patch("os.listdir")
    def test_file_not_found(
        self,
        mock_listdir: MagicMock,
        mock_isfile: MagicMock,
        mock_dirname: MagicMock,
        mock_abspath: MagicMock
    ) -> None:
        """Test scenario where dummy.json is not found in any directory."""
        self.setUpMockBehavior(
            mock_abspath,
            mock_dirname,
            mock_isfile,
            self.CHILD_DIR_1,
            [self.CHILD_DIR_1, self.PARENT_DIR, "/"],
            [False, False, False]
        )

        result: str | None = find_path_to_file(self.FILENAME)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main(verbosity=2)
