
import unittest
from unittest.mock import patch, MagicMock
from typing import Optional
from jgh_logger import validate_logfile_particulars, LogFilePathSegmentCompendium, LogFilePathCompendium

class TestValidateLogfileParticulars(unittest.TestCase):

    def test_valid_logfile_particulars(self) -> None:
        """
        Test with valid logfile particulars.
        """
        segments_compendium = LogFilePathSegmentCompendium(
            storage_dirpath="/logs",
            debug_filename="debug.log",
            info_filename="info.log",
            warning_filename="warning.log",
            error_filename="error.log",
            critical_filename="critical.log"
        )
        with patch("os.path.isabs", return_value=True), patch("os.path.exists", return_value=True):
            result: Optional[LogFilePathCompendium] = validate_logfile_particulars(segments_compendium)
            self.assertIsNotNone(result)
            self.assertEqual(result.debug_level_file, "/logs/debug.log")
            self.assertEqual(result.info_level_file, "/logs/info.log")
            self.assertEqual(result.warning_level_file, "/logs/warning.log")
            self.assertEqual(result.error_level_file, "/logs/error.log")
            self.assertEqual(result.critical_level_file, "/logs/critical.log")

    def test_missing_storage_dirpath(self) -> None:
        """
        Test with missing storage_dirpath.
        """
        segments_compendium = LogFilePathSegmentCompendium(
            storage_dirpath=None,
            debug_filename="debug.log",
            info_filename="info.log",
            warning_filename="warning.log",
            error_filename="error.log",
            critical_filename="critical.log"
        )
        result: Optional[LogFilePathCompendium] = validate_logfile_particulars(segments_compendium)
        self.assertIsNone(result)

    def test_relative_storage_dirpath(self) -> None:
        """
        Test with relative storage_dirpath.
        """
        segments_compendium = LogFilePathSegmentCompendium(
            storage_dirpath="relative/path",
            debug_filename="debug.log",
            info_filename="info.log",
            warning_filename="warning.log",
            error_filename="error.log",
            critical_filename="critical.log"
        )
        with patch("os.path.isabs", return_value=False):
            result: Optional[LogFilePathCompendium] = validate_logfile_particulars(segments_compendium)
            self.assertIsNone(result)

    def test_nonexistent_storage_dirpath(self) -> None:
        """
        Test with nonexistent storage_dirpath.
        """
        segments_compendium = LogFilePathSegmentCompendium(
            storage_dirpath="/nonexistent/path",
            debug_filename="debug.log",
            info_filename="info.log",
            warning_filename="warning.log",
            error_filename="error.log",
            critical_filename="critical.log"
        )
        with patch("os.path.isabs", return_value=True), patch("os.path.exists", return_value=False):
            result: Optional[LogFilePathCompendium] = validate_logfile_particulars(segments_compendium)
            self.assertIsNone(result)

    def test_invalid_filenames(self) -> None:
        """
        Test with invalid filenames.
        """
        segments_compendium = LogFilePathSegmentCompendium(
            storage_dirpath="/logs",
            debug_filename="debug.txt",
            info_filename="info.txt",
            warning_filename="warning.txt",
            error_filename="error.txt",
            critical_filename="critical.txt"
        )
        with patch("os.path.isabs", return_value=True), patch("os.path.exists", return_value=True):
            result: Optional[LogFilePathCompendium] = validate_logfile_particulars(segments_compendium)
            self.assertIsNone(result)

    def test_all_filenames_none(self) -> None:
        """
        Test with all filenames set to None.
        """
        segments_compendium = LogFilePathSegmentCompendium(
            storage_dirpath="/logs",
            debug_filename=None,
            info_filename=None,
            warning_filename=None,
            error_filename=None,
            critical_filename=None
        )
        with patch("os.path.isabs", return_value=True), patch("os.path.exists", return_value=True):
            result: Optional[LogFilePathCompendium] = validate_logfile_particulars(segments_compendium)
            self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main(verbosity=2)
