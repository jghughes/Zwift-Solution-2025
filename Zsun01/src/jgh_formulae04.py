
from typing import Dict, List, Tuple
from zwiftrider_item import ZwiftRiderItem


def compose_map_of_rider_work_assignments(riders: List[ZwiftRiderItem], pull_durations: List[float]) -> Dict[ZwiftRiderItem, List[Tuple[int, float]]]:
    """
    Generates a mapping for a team of riders in a Team Time Trial race to their workloads. 
    Riders circulate in a cyclical pattern in a pace line, with each rider taking a turn 
    at the front (a pull) and then rotating to the back squentially. The sequence
    of pulls is according to pull_durations list. Each rider has as many 
    workunits as there are position/riders in the circulating pace line. Each workunit 
    is a tuple of the prevailing position of the rider in the pace line and the 
    pull duration of the prevailing leader at the front of the pace line.

    Args:
        riders (List[ZwiftRiderItem]): The list of Zwift riders.
        pull_durations (List[float]): The list of pull durations.

    Returns:
        Dict[ZwiftRiderItem, List[Tuple[int, float]]]: A dictionary of Zwift riders with
            their list of respective workunit parameters. The Tuple for a workunit
            is (position, duration).
    """
    n = len(riders)
    rider_workunits: Dict[ZwiftRiderItem, List[Tuple[int, float]]] = {}
    for k in range(1, n + 1):
        workunits: List[Tuple[int, float]] = []
        for j in range(n):
            position = (k + n - j - 1) % n + 1
            duration = pull_durations[j]
            workunits.append((position, duration))
        rider_workunits[riders[k - 1]] = workunits
    return rider_workunits

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
    mapping = compose_map_of_rider_work_assignments(riders, pull_durations)

    # Display the outcome using tabulate
    table = []
    for rider, tasks in mapping.items():
        for position, duration in tasks:
            table.append([rider.name, position, duration])

    headers = ["Rider", "Position", "Pull Duration"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    main()
