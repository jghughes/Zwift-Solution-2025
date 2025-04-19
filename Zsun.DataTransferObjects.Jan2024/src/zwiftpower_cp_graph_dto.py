from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, List, Any, Union


class ZwiftPowerCpGraphDTO(BaseModel):
    """
    A data transfer object representing a Zwift Power Graph JSON object. The property
    names in the class and its nested classes precisely match the names in the JSON
    from ZwiftPower.

    Each rider in ZwiftPower is represented as a standalone file, scraped from the
    ZwiftPower website by DaveK. The name of each file corresponds to the ZwiftID
    of the rider. There is no ID contained in the file that ties back to the rider.
    You have to rely on the filename.

    This DTO focuses on the power data contained in the `efforts` dictionary. The
    dictionary has three keys (str):
    - "30days": A list of efforts over the last 30 days.
    - "90days": A list of efforts over the last 90 days.
    - or a wrapped int ID for the most recent event.

    Each key contains a list of `EffortItemDTO` objects. 

    Attributes:
        info (List[InfoItemDTO]): A list of metadata items about the rider's efforts.
        efforts (Dict[str, List[EffortItemDTO]]): A dictionary of effort data, where
            keys are "30days", "90days", or the most recent event ID, and values are
            lists of `EffortItemDTO` objects.
        events (Dict[str, Any]): A dictionary of event-related data (not used).
        zwiftpower_watts_last_updated (str): The timestamp of the last update for
            ZwiftPower watts data.
    """

    class InfoItemDTO(BaseModel):
        """
        Represents a line-item in the 'info' list. A nested class.

        Attributes:
            name (str): The name of the effort (e.g., "Last 30 days").
            effort_id (Union[str, int]): The identifier for the effort (e.g., "30days"), or the int ID of the event.
            hide (bool): Whether the effort is hidden.
        """
        name:      Optional[str] = ""
        effort_id: Optional[Union[str,int]] = ""
        hide:      Optional[bool] = False

    class EffortItemDTO(BaseModel):
        """
        Represents a line-item in the lists that are the values of the three
        keys in the 'efforts' dictionary. A nested class.

        Attributes:
            x (int): The X coordinate (time in seconds).
            y (int): The Y coordinate (power in watts).
            date (int): The timestamp of the effort.
            zid (str): The event ID, linked to a list of events (not used).
        """
        x:    Optional[int] = 0
        y:    Optional[int] = 0
        date: Optional[int] = 0
        zid:  Optional[str] = ""

    model_config = ConfigDict(
        alias_generator=None,      # No alias generator for this DTO
        populate_by_name=True      # Allow population by field names
    )
    info:                          Optional[Union[List[InfoItemDTO], Any]] = Field(default_factory=list)
    efforts:                       Optional[Union[Dict[str, List[EffortItemDTO]],Any]] = Field(default_factory=dict)
    events:                        Optional[Union[Dict[str, Any],Any]] = Field(default_factory=dict)
    zwiftpower_watts_last_updated: Optional[str] = ""

