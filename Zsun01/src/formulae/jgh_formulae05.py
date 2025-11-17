"""
Paceline Rider Exertion Formulae
================================

This module provides functions for calculating and managing rider
exertions in cycling paceline simulations. It projects rider work
assignments into detailed exertion records, including speed, duration,
wattage, and energy expenditure for each segment of a paceline
rotation.

Key Features:
-------------
- Computes rider exertion profiles from work assignments, including
  position, speed, duration, wattage, and kilojoules.
- Estimates power requirements and energy expenditure for each rider
  in the paceline using physics-based models.
- Supports tabular logging of rider exertion data for analysis and
  debugging.

Functions:
----------
- populate_rider_exertions(rider_work_assignments): Generate exertion
  records for each rider based on their work assignments.
- log_rider_exertions(test_description, result): Log rider exertion
  data in a tabular format.

Notes:
------
- Logging is forbidden in functions called during parallel processing.

Example Usage:
--------------
    exertions = populate_rider_exertions(work_assignments)
    log_rider_exertions("Exertion report", exertions)
"""

from collections import defaultdict
from typing import Dict, List
from working_types import RiderExertionItem, RiderWorkAssignmentItem
from jgh_formulae01 import estimate_kilojoules_from_wattage_and_time
from jgh_formulae02 import calculate_wattage_riding_in_the_paceline
from rider_brute_item import RiderBruteItem

# This function called during parallel processing. Logging forbidden
def populate_rider_exertions(rider_work_assignments: Dict[RiderBruteItem, List[RiderWorkAssignmentItem]]) -> Dict[RiderBruteItem, List[RiderExertionItem]]:
    """
    Projects the rider_work_assignments dict to a new dict of rider_workloads with additional wattage calculation.
    
    Args:
        speed (float): The speed of the paceline.
        rider_work_assignments (Dict[RiderBruteItem, List[RiderWorkAssignmentItem]): The dictionary of rider workunits.

    Returns:
        Dict[RiderBruteItem, List[RiderExertionItem]]: A dictionary of Zwift riders with
            their list of respective efforts including wattage. The Tuple representing 
            a single workload is (position, speed, duration, wattage). Each rider has a list of dict_of_rider_exertions
    """
    rider_workloads: Dict[RiderBruteItem, List[RiderExertionItem]] = defaultdict(list)
    
    for rider, dict_of_rider_work_assignments in rider_work_assignments.items():
        dict_of_rider_exertions: List[RiderExertionItem] = []
        for assignment in dict_of_rider_work_assignments:
            wattage = calculate_wattage_riding_in_the_paceline(rider, assignment.speed, assignment.position)
            kilojoules = estimate_kilojoules_from_wattage_and_time(wattage, assignment.duration)

            dict_of_rider_exertions.append(RiderExertionItem(current_location_in_paceline=assignment.position, speed_kph=assignment.speed, duration=assignment.duration, wattage=wattage, kilojoules=kilojoules))
        rider_workloads[rider] = dict_of_rider_exertions
    
    return rider_workloads

def log_rider_exertions(test_description: str, result: Dict[RiderBruteItem, List[RiderExertionItem]]) -> None:
    from tabulate import tabulate
    print(test_description)
    table = []
    for rider, efforts in result.items():
        for effort in efforts:
            table.append([
                rider.name, 
                effort.current_location_in_paceline, 
                round(effort.speed_kph, 1), 
                round(effort.duration), 
                round(effort.wattage, 0), 
                round(effort.kilojoules, 0)
            ])

    headers = [
        "rider", 
        "location", 
        "kph", 
        "seconds", 
        "watts", 
        "kJ"
    ]
    print("\n" + tabulate(table, headers=headers, tablefmt="plain",disable_numparse=True))

