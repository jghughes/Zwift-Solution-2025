
import os
import unittest
from unittest.mock import patch
from typing import Optional
from jgh_logger import validate_logfile_settings, LogFilePathSegmentCompendium, LogFilePathCompendium

groovy_dirPath = r"C:\Users\johng\holding_pen\Test_scratchpad\LogFiles"

class TestValidateLogfileParticulars(unittest.TestCase):

    def test_valid_logfile_particulars(self) -> None:
        """
        Test with valid logfile particulars.
        """
        segments_compendium = LogFilePathSegmentCompendium(
            storage_dirpath=groovy_dirPath,
            debug_filename="debug.log",
            info_filename="info.log",
            warning_filename="warning.log",
            error_filename="error.log",
            critical_filename="critical.log"
        )
        with patch("os.path.isabs", return_value=True), patch("os.path.exists", return_value=True):
            filepaths: Optional[LogFilePathCompendium] = validate_logfile_settings(segments_compendium)
            self.assertIsNotNone(filepaths)
            self.assertEqual(filepaths.debug_filepath, os.path.join(groovy_dirPath, "debug.log"))
            self.assertEqual(filepaths.info_filepath, os.path.join(groovy_dirPath, "info.log"))
            self.assertEqual(filepaths.warning_filepath, os.path.join(groovy_dirPath, "warning.log"))
            self.assertEqual(filepaths.error_filepath, os.path.join(groovy_dirPath, "error.log"))
            self.assertEqual(filepaths.critical_filepath, os.path.join(groovy_dirPath, "critical.log"))




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
        filepaths: Optional[LogFilePathCompendium] = validate_logfile_settings(segments_compendium)
        self.assertIsNone(filepaths)

    # def test_relative_storage_dirpath(self) -> None:
    #     """
    #     Test with relative storage_dirpath.
    #     """
    #     # relative_dirpath = os.getcwd() # absolute path of current working directory
    #     rel_dirpath = os.curdir # relative path of current working directory i.e. "."
    #     rel_dirpath = os.path.join(os.curdir, "..")  # one level up
    #     rel_dirpath = os.path.join(os.curdir, "..", "..")  # two levels up

    #     segments_compendium = LogFilePathSegmentCompendium(
    #         storage_dirpath=rel_dirpath,
    #         debug_filename="debug.log",
    #         info_filename="info.log",
    #         warning_filename="warning.log",
    #         error_filename="error.log",
    #         critical_filename="critical.log"
    #     )
    #     with patch("os.path.isabs", return_value=False):
    #         filepaths: Optional[LogFilePathCompendium] = validate_logfile_settings(segments_compendium)
    #         self.assertIsNone(filepaths)

    def test_nonexistent_storage_dirpath(self) -> None:
        """
        Test with nonexistent storage_dirpath.
        """
        segments_compendium = LogFilePathSegmentCompendium(
            storage_dirpath="rubbish/nonexistent/path",
            debug_filename="debug.log",
            info_filename="info.log",
            warning_filename="warning.log",
            error_filename="error.log",
            critical_filename="critical.log"
        )
        with patch("os.path.isabs", return_value=True), patch("os.path.exists", return_value=False):
            filepaths: Optional[LogFilePathCompendium] = validate_logfile_settings(segments_compendium)
            self.assertIsNone(filepaths)

    def test_invalid_filenames(self) -> None:
        """
        Test with invalid filenames.
        """
        segments_compendium = LogFilePathSegmentCompendium(
            storage_dirpath=groovy_dirPath,
            debug_filename="debug.txt",
            info_filename="info.txt",
            warning_filename="warning.txt",
            error_filename="error.txt",
            critical_filename="critical.txt"
        )
        with patch("os.path.isabs", return_value=True), patch("os.path.exists", return_value=True):
            filepaths: Optional[LogFilePathCompendium] = validate_logfile_settings(segments_compendium)
            self.assertIsNone(filepaths)

    def test_all_filenames_none(self) -> None:
        """
        Test with all filenames set to None.
        """
        segments_compendium = LogFilePathSegmentCompendium(
            storage_dirpath=groovy_dirPath,
            debug_filename=None,
            info_filename=None,
            warning_filename=None,
            error_filename=None,
            critical_filename=None
        )
        with patch("os.path.isabs", return_value=True), patch("os.path.exists", return_value=True):
            filepaths: Optional[LogFilePathCompendium] = validate_logfile_settings(segments_compendium)
            self.assertIsNone(filepaths)

if __name__ == "__main__":
    unittest.main(verbosity=2)
