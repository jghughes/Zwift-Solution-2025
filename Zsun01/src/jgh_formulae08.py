from typing import List, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor
from jgh_formulae04 import RiderWorkAssignmentItem
from jgh_formulae05 import RiderEffortItem
from jgh_formulae07 import calculate_rider_aggregate_efforts, calculate_rider_stress_metrics, log_rider_aggregate_efforts, log_rider_stress_metrics

from zwiftrider_item import ZwiftRiderItem

def generate_rider_power_datapoints_for_one_hour(efforts: List[RiderEffortItem]) -> List[Tuple[int, float]]:
    """
    Generate rider power datapoints for one hour.

    Args:
        efforts (List[RiderEffortItem]): List of rider efforts.

    Returns:
        List[Tuple[int, float]]: List of power datapoints for one hour.
    """
    # Step 1: Generate a succession of repetitions of the input list of RiderEffortItem
    total_duration = sum(effort.duration for effort in efforts)
    repetitions = int((3600 // total_duration) + 1)
    extended_efforts: List[RiderEffortItem] = [effort for _ in range(repetitions) for effort in efforts]
    
    # Step 2: Generate a datapoint of (t, wattage) for every second up until t=3600
    datapoints: List[Tuple[int, float]] = [(0, 0.0)] * 3601  # Preallocate list with 3601 elements
    current_time: int = 0
    effort_index: int = 0
    current_effort: RiderEffortItem = extended_efforts[effort_index]
    effort_time: int = 0
    
    while current_time <= 3600:
        if effort_time >= current_effort.duration:
            effort_index += 1
            current_effort = extended_efforts[effort_index]
            effort_time = 0
        
        datapoints[current_time] = (current_time, current_effort.wattage)
        current_time += 1
        effort_time += 1
    
    return datapoints[:3600]  # Ensure the list is exactly 3600 elements long

def segment_data(datapoints: List[Tuple[int, float]], segment_durations: List[int]) -> Dict[int, float]:
    """
    Segment the data into specified durations and calculate the maximum average power for each segment.

    Args:
        datapoints (List[Tuple[int, float]]): List of power datapoints for one hour.
        segment_durations (List[int]): List of segment durations in seconds.

    Returns:
        Dict[int, float]: Dictionary where keys are segment durations and values are maximum average power outputs.
    """
    segmented_data: Dict[int, float] = {}

    for duration in segment_durations:
        max_avg_power: float = 0.0
        num_intervals: int = 3600 - duration + 1

        # Calculate the sum of the first interval
        interval_sum: float = sum(datapoints[j][1] for j in range(duration))
        max_avg_power = interval_sum / duration

        # Use sliding window technique to calculate the sum of subsequent intervals
        for i in range(1, num_intervals):
            interval_sum = interval_sum - datapoints[i - 1][1] + datapoints[i + duration - 1][1]
            avg_power: float = interval_sum / duration
            if avg_power > max_avg_power:
                max_avg_power = avg_power

        segmented_data[duration] = max_avg_power

    return segmented_data

def process_rider(rider: ZwiftRiderItem, rider_efforts: Dict[ZwiftRiderItem, List[RiderEffortItem]], segment_durations: List[int]) -> Dict[int, float]:
    """
    Process the data for a single rider.

    Args:
        rider (ZwiftRiderItem): The rider to process.
        rider_efforts (Dict[ZwiftRiderItem, List[RiderEffortItem]]): Dictionary of rider efforts.
        segment_durations (List[int]): List of segment durations in seconds.

    Returns:
        Dict[int, float]: Segmented data for the rider.
    """
    rider_power_datapoints = generate_rider_power_datapoints_for_one_hour(rider_efforts[rider])
    segmented_data = segment_data(rider_power_datapoints, segment_durations)
    return segmented_data

# Example usage in the main function
def main() -> None:

    # Configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_efforts
    from handy_utilities import get_all_zwiftriders

    # Define constituents of one or more scenarios (4 pull speed scenarios in this case))

    dict_of_zwiftrideritem = get_all_zwiftriders()

    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    joshn : ZwiftRiderItem = dict_of_zwiftrideritem['joshn']
    richardm : ZwiftRiderItem = dict_of_zwiftrideritem['richardm']
    
    riders : list[ZwiftRiderItem] = [barryb, johnh, joshn, richardm]
    pull_duration_scenario = [120.0, 60.0, 60.0, 30.0]
    pull_speed_scenarios = [
        # [37.5, 37.5, 37.5, 37.5],
        [40.0, 40.0, 40.0, 40.0],
        # [42.5, 42.5, 42.5, 42.5],
        # [45.0, 45.0, 45.0, 45.0]
    ]
    # Segment durations
    # # segment_durations: List[int] = [30, 60, 90, 120, 2400, 3600]
    segment_durations: List[int] = [5, 15, 30, 60, 120, 180, 300, 600, 720, 900, 1200, 1800, 2400, 3600]

    # Compose the rider work_assignments, then work_efforts, then aggregate_efforts, and then stress_metrics for each scenario

    for i, pull_speed_scenario in enumerate(pull_speed_scenarios):
        work_assignments : Dict[ZwiftRiderItem, List[RiderWorkAssignmentItem]] = populate_rider_work_assignments(riders, pull_duration_scenario, pull_speed_scenario)

        #log work assignments for riders
        # for rider in riders:
        #     logger.info(f"\n{rider.name}")
        #     for assignment in work_assignments[rider]:
        #         logger.info(f"position: {assignment.position} for {assignment.duration}sec @ {assignment.speed}km/h")

        rider_efforts = populate_rider_efforts(work_assignments)

        #log work efforts for riders
        for rider in riders:
            logger.info(f"\n{rider.name}")
            for effort in rider_efforts[rider]:
                logger.info(f"position: {effort.position} for {effort.duration}sec @{effort.speed}km/h  output: {effort.wattage}W")

        # Generate dict of riders with rider power datapoints for one hour
        rider_power_datapoints : Dict[ZwiftRiderItem, List[Tuple[int, float]]] = {}
        for rider in riders:
            rider_power_datapoints[rider] = generate_rider_power_datapoints_for_one_hour(rider_efforts[rider])
            # #log the rider power datapoints for the first 30 datapoints for each rider
            # logger.info(f"\n{rider.name}")
            # for datapoint in rider_power_datapoints[rider][:30]:
            #     logger.info(f"{datapoint[0]}sec: {datapoint[1]:.2f}W")

        # Generate dict of riders with segmented data rider power datapoints for one hour in parallel
        segmented_data: Dict[ZwiftRiderItem, Dict[int, float]] = {}
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_rider, rider, rider_efforts, segment_durations): rider for rider in riders}
            for future in futures:
                rider = futures[future]
                segmented_data[rider] = future.result()

        # Log the segmented data i.e. the rough and ready power curve for each rider!!
        for rider, data in segmented_data.items():
            logger.info(f"\n{rider.name}")
            for duration, avg_power in data.items():
                logger.info(f"{duration}sec: {avg_power:.1f}W")

        # rider_aggregate_efforts = calculate_rider_aggregate_efforts(rider_efforts)
        # rider_stress_metrics = calculate_rider_stress_metrics(rider_aggregate_efforts)

        # total_duration = next(iter(rider_aggregate_efforts.values())).total_duration
        # average_speed = next(iter(rider_aggregate_efforts.values())).average_speed #  #careful. formula below only valid when speed is constant, as it is in this case
        # total_distance = next(iter(rider_aggregate_efforts.values())).total_distance

        # table_heading= f"\nPull durations={pull_duration_scenario}sec\nPull speeds={pull_speed_scenarios[i]}km/h\nTotal_duration={total_duration}  Ave_speed={average_speed}  Total_dist={total_distance}"
        # log_rider_aggregate_efforts(table_heading, rider_aggregate_efforts, logger)

        # log_rider_stress_metrics(f"", rider_stress_metrics, logger)
        
if __name__ == "__main__":
    main()
