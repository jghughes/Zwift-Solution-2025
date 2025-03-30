from typing import List, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor
from zwiftrider_item import ZwiftRiderItem
from zwiftrider_related_items import RiderWorkAssignmentItem, RiderWorkItem, RiderCriticalPowerItem

def translate_efforts_to_wattages_per_second_for_one_hour(efforts: List[RiderWorkItem]) -> List[Tuple[int, float]]:
    """
    Generate rider power datapoints for one hour.

    Args:
        efforts (List[RiderWorkItem]): List of rider efforts.

    Returns:
        List[Tuple[int, float]]: List of power datapoints for one hour.
    """
    # Step 1: Generate a succession of repetitions of the input list of RiderWorkItem
    total_duration = sum(effort.duration for effort in efforts)
    repetitions = int((3600 // total_duration) + 1)
    extended_efforts: List[RiderWorkItem] = [effort for _ in range(repetitions) for effort in efforts]
    
    # Step 2: Generate a datapoint of (t, wattage) for every second up until t=3600
    datapoints: List[Tuple[int, float]] = [(0, 0.0)] * 3601  # Preallocate list with 3601 elements
    current_time: int = 0
    effort_index: int = 0
    current_effort: RiderWorkItem = extended_efforts[effort_index]
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

def translate_efforts_into_criticalpower_item(rider: ZwiftRiderItem, rider_efforts: Dict[ZwiftRiderItem, List[RiderWorkItem]], cp_test_duration_specs: List[int]) -> RiderCriticalPowerItem:
    """
    Calculate the critical power curve for a single rider.

    Args:
        rider (ZwiftRiderItem): The rider to process.
        rider_efforts (Dict[ZwiftRiderItem, List[RiderWorkItem]]): Dictionary of rider efforts which record intervals of duration and power exerted.
        cp_test_duration_specs (List[int]): List of timespans for each of the desired datapoints in the power curve in seconds.

    Returns:
        Dict[int, float]: CriticalPower curve data for the rider where int is the number of seconds of the timespan and float is the wattage.
    """
    wattage_datapoints = translate_efforts_to_wattages_per_second_for_one_hour(rider_efforts[rider])

    powercurve_datapoints = distill_cp_metrics_from_wattages_per_second(wattage_datapoints, cp_test_duration_specs)

    # map the critical power curve to the rider in the form of a CriticalPowerCurveItem
    critical_power_curve = CriticalPowerCurveItem(
        cpw_5_sec=powercurve_datapoints.get(5, 0.0),
        cpw_15_sec=powercurve_datapoints.get(15, 0.0),
        cpw_30_sec=powercurve_datapoints.get(30, 0.0),
        cpw_1_min=powercurve_datapoints.get(60, 0.0),
        cpw_2_min=powercurve_datapoints.get(120, 0.0),
        cpw_3_min=powercurve_datapoints.get(180, 0.0),
        cpw_5_min=powercurve_datapoints.get(300, 0.0),
        cpw_10_min=powercurve_datapoints.get(600, 0.0),
        cpw_12_min=powercurve_datapoints.get(720, 0.0),
        cpw_15_min=powercurve_datapoints.get(900, 0.0),
        cpw_20_min=powercurve_datapoints.get(1200, 0.0),
        cpw_30_min=powercurve_datapoints.get(1800, 0.0),
        cpw_40_min=powercurve_datapoints.get(2400, 0.0)
    )

    return critical_power_curve


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
    pull_duration_scenario = [120.0, 90.0, 60.0, 30.0]
    pull_speed_scenarios = [
        # [37.5, 37.5, 37.5, 37.5],
        [40.0, 40.0, 40.0, 40.0],
        # [42.5, 42.5, 42.5, 42.5],
        # [45.0, 45.0, 45.0, 45.0]
    ]
    # Segment durations
    cp_test_duration_specs: List[int] = [5, 15, 30, 60, 120, 180, 300, 600, 720, 900, 1200, 1800, 2400, 3600]

    # Compose the rider work_assignments, then work_efforts, then aggregate_efforts, and then stress_metrics for each scenario

    for i, pull_speed_scenario in enumerate(pull_speed_scenarios):
        work_assignments : Dict[ZwiftRiderItem, List[RiderWorkAssignmentItem]] = populate_rider_work_assignments(riders, pull_duration_scenario, pull_speed_scenario)

        #log work assignments for riders
        # for rider in riders:
        #     logger.info(f"\n{rider.name}")
        #     for assignment in work_assignments[rider]:
        #         logger.info(f"position: {assignment.position} for {assignment.duration}sec @ {assignment.speed}km/h")

        rider_efforts = populate_rider_efforts(work_assignments)

        # #log work efforts for riders
        # for rider in riders:
        #     logger.info(f"\n{rider.name}")
        #     for effort in rider_efforts[rider]:
        #         logger.info(f"position: {effort.position} for {effort.duration}sec @{effort.speed}km/h  output: {effort.wattage:.1f}W")

        # Generate dict of riders with rider power datapoints for one hour
        wattage_datapoints : Dict[ZwiftRiderItem, List[Tuple[int, float]]] = {}
        for rider in riders:
            wattage_datapoints[rider] = translate_efforts_to_wattages_per_second_for_one_hour(rider_efforts[rider])
            # #log the rider power datapoints for the first 30 datapoints for each rider
            # logger.info(f"\n{rider.name}")
            # for datapoint in wattage_datapoints[rider][:30]:
            #     logger.info(f"{datapoint[0]}sec: {datapoint[1]:.1f}W")

        # Generate dict of riders with their critical power curve
        dict_of_riders_and_their_criticalpower_curve: Dict[ZwiftRiderItem, CriticalPowerCurveItem] = {}
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(translate_efforts_into_criticalpower_item, rider, rider_efforts, cp_test_duration_specs): rider for rider in riders}
            for future in futures:
                rider = futures[future]
                dict_of_riders_and_their_criticalpower_curve[rider] = future.result()

        # Log power curve for each rider
        for rider, data in dict_of_riders_and_their_criticalpower_curve.items():
            logger.info(f"\n{rider.name}")
            #log the value of all attrs of the rider's critical power curve
            for key, value in data.__dict__.items():
                logger.info(f"{key}: {value:.1f}W")

        a,b = estimate_cp_and_w_prime()

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
