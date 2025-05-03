from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Union
from jgh_read_write import *
from jgh_serialization import *


class EffortDTO(BaseModel):
    x    : Optional[int] = 0    # X-coordinate
    y    : Optional[int] = 0    # Y-coordinate
    date : Optional[int] = 0    # Date as a Unix timestamp
    zid  : Optional[str] = ""   # Zwift ID

# this class is used for inputting from DaveK source data. it only extracts the effort data. it leaves all the other stuff behind
class ZwiftPowerBestPowerDTO(BaseModel):
    efforts : Optional[Union[Dict[str, List[EffortDTO]], Any]] = Field(default_factory=dict)  # Efforts dictionary

def main():

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    import os
    from typing import cast
    from jgh_read_write import read_filepath_as_text, help_select_filepaths_in_folder
    from jgh_serialization import JghSerialization

    ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    file_paths = help_select_filepaths_in_folder(None,".json", ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH)
    logger.info(f"Found {len(file_paths)} files in {ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH}")
    file_count = 0
    error_count = 0
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftPowerBestPowerDTO)
            dto = cast(ZwiftPowerBestPowerDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
    logger.info(f"Successfully processed {file_count} files")
    logger.info(f"Encountered {error_count} errors during processing")

if __name__ == "__main__":
    main()



