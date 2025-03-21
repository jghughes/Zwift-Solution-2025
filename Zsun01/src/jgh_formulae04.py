
from typing import Dict, List, Tuple
from zwiftrider_item import ZwiftRiderItem


def generate_rider_workunit_mapping(riders: List[ZwiftRiderItem], pull_durations: List[float]) -> Dict[ZwiftRiderItem, List[Tuple[int, float]]]:
    """
    Generates a mapping for a team of riders in a Team Time Trial race. The riders 
    circulate in a cyclical pattern, with each rider taking a turn at the front 
    and then rotating to the back of the pace line, and so on. The duration for each pull 
    at the front is specified in the pull_durations list. Each rider has as many 
    workunits as there are position/riders in the circulating pace line. Each workunit 
    is a tuple of the prevailing position of the rider in the pace line and the 
    pull duration of the prevailing leader at the front of the pace line.

    Args:
        riders (List[ZwiftRiderItem]): The list of Zwift riders.
        pull_durations (List[float]): The list of pull durations.

    Returns:
        Dict[ZwiftRiderItem, List[Tuple[int, float]]]: A dictionary of Zwift riders with
            their list of respective workunits.
    """
    n = len(riders)
    mapping: Dict[ZwiftRiderItem, List[Tuple[int, float]]] = {}
    for k in range(1, n + 1):
        rider_workunits: List[Tuple[int, float]] = []
        for j in range(n):
            position = (k + n - j - 1) % n + 1
            pull_duration = pull_durations[j]
            rider_workunits.append((position, pull_duration))
        mapping[riders[k - 1]] = rider_workunits
    return mapping

# Example usage:
def main() -> None:
    # Configure logging
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from typing import Dict, cast
    from jgh_read_write import read_text
    from jgh_serialization import JghSerialization
    from zwiftrider_dto import ZwiftRiderDataTransferObject
    from tabulate import tabulate

    # Load rider data from JSON
    inputjson = read_text("C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/", "rider_dictionary.json")
    dict_of_zwiftrider_dto= JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDataTransferObject])

    # for the benfit of type inference: explicitly cast the return value of the serialisation to expected generic Type
    dict_of_zwiftrider_dto = cast(Dict[str, ZwiftRiderDataTransferObject], dict_of_zwiftrider_dto)

    #transform to ZwiftRiderItem dict
    dict_of_zwiftrideritem = ZwiftRiderItem.from_dataTransferObject_dict(dict_of_zwiftrider_dto)

    # Instantiate ZwiftRiderItem objects for barryb, johnh, and lynseys
    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    lynseys : ZwiftRiderItem = dict_of_zwiftrideritem['lynseys']

    # Create a list of the selected riders
    riders : list[ZwiftRiderItem] = [barryb, johnh, lynseys]

    # Example riders and pull durations
    pull_durations = [90.0, 60.0, 30.0]

    # Generate the rider-workunit mapping
    mapping = generate_rider_workunit_mapping(riders, pull_durations)

    # Display the outcome using tabulate
    table = []
    for rider, tasks in mapping.items():
        for position, duration in tasks:
            table.append([rider.name, position, duration])

    headers = ["Rider", "Position", "Pull Duration"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    main()
