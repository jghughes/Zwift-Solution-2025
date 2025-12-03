"""
Paceline Work Assignment Formulae
=================================

This module provides functions for generating and managing rider work
assignments in cycling team time trial simulations. It models the
cyclical rotation of riders in a paceline, assigning each rider a
sequence of work units that specify their position, duration, and
speed for each pull.

Key Features:
-------------
- Generates detailed work assignments for each rider in a paceline
  based on input pull durations and speeds.
- Models the cyclical rotation of riders, ensuring each rider takes
  turns at the front and rotates to the tail.
- Supports flexible input lengths for pull durations and speeds.
- Provides tabular logging of rider assignments for analysis and
  debugging.

Functions:
----------
- populate_rider_work_assignments(riders, pull_durations,
  pull_speeds_kph): Generate work assignments for each rider.
- log_rider_work_assignments(test_description, result): Log rider
  assignments in a tabular format.

Notes:
------
- Logging is forbidden in functions called during parallel processing.

Example Usage:
--------------
    assignments = populate_rider_work_assignments(riders,
        [120.0, 120.0, 120.0, 120.0], [40.0, 40.0, 40.0, 40.0])
"""

from collections import defaultdict
from typing import Dict, List

from paceline_computation_types import RiderWorkAssignmentItem
from rider_brute_item import RiderBruteItem

# This function called during parallel processing. Logging forbidden
def populate_rider_work_assignments(riders: List[RiderBruteItem], pull_durations: List[float], pull_speeds_kph: List[float]) -> Dict[RiderBruteItem, List[RiderWorkAssignmentItem]]:
    """
    Generates a mapping for a team of riders in a Team Time Trial race to their workloads. 
    Riders circulate in a cyclical pattern in a paceline, with each rider taking a turn 
    at the head (a pull) and then rotating to the tail sequentially. The sequence
    of pulls is according to pull_durations and pull_speeds_kph lists. Each rider has as many 
    workunits as there are positions/riders in the circulating paceline. Each workunit 
    is an instance of RiderWorkAssignmentItem according to position of the rider 
    in the paceline, and his duration and speed in that position as dictated 
    by the duarion and speed of the prevailing leader at that point in time.

    Args:
        riders (List[RiderBruteItem]): The list of Zwift riders from head to tail.
        pull_durations (List[float]): The list of pull durations from head to tail.
        pull_speeds_kph (List[float]): The list of pull speeds from head to tail.

    Returns:
        Dict[RiderBruteItem, List[RiderWorkAssignmentItem]]: A dictionary of Zwift riders 
            with their list of respective assignments, being how fast they must go for 
            how long in which position. 
    """
    n = len(riders)

    if n == 0:
        return defaultdict(list)

    if len(pull_durations) == 0 or len(pull_speeds_kph) == 0:
        dd : Dict[RiderBruteItem, List[RiderWorkAssignmentItem]] = defaultdict(list)
        for rider in riders:
            dd[rider] = [RiderWorkAssignmentItem()]
        return dd

    min_length = min(len(pull_durations), len(pull_speeds_kph))

    rider_workunits: Dict[RiderBruteItem, List[RiderWorkAssignmentItem]] = defaultdict(list)
    for k in range(1, n + 1):
        workunits: List[RiderWorkAssignmentItem] = []
        for j in range(n):
            # The formula ensures that each rider's position is calculated in a way that 
            # they rotate through the pace line in a cyclical manner. The modulo operation 
            # handles the wrap-around, and the addition of 1 converts the result to a 1-based index.
            position = (k + n - j - 1) % n + 1
            if j < min_length:
                duration = pull_durations[j]
                speed = pull_speeds_kph[j]
                workunit = RiderWorkAssignmentItem(position=position, duration=duration, speed=speed)
            else:
                workunit = RiderWorkAssignmentItem(position=position)
            workunits.append(workunit)
        rider_workunits[riders[k - 1]] = workunits
    return rider_workunits

def log_rider_work_assignments(test_description: str, result: Dict[RiderBruteItem, List[RiderWorkAssignmentItem]]) -> None:
    from tabulate import tabulate

    table: list[list[object]] = []

    for rider, assignments in result.items():
        for assignment in assignments:
            table.append([
                rider.name, 
                assignment.position, 
                assignment.duration, 
                assignment.speed
            ])

    headers = [
        "Rider", 
        "Position", 
        "Duration (sec)", 
        "Speed (kph)"
    ]
    print(f"{test_description}:\n" + tabulate(table, headers=headers, tablefmt="plain",disable_numparse=True))

