from zwiftrider_item import ZwiftRiderItem
from jgh_formulae07 import calculate_rider_aggregate_efforts, calculate_rider_stress_metrics, log_rider_aggregate_efforts, log_rider_stress_metrics

# Example usage in the main function
def main() -> None:

    # Configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from jgh_formulae04 import compose_map_of_rider_work_assignments
    from jgh_formulae05 import populate_map_of_rider_efforts
    from handy_utilities import get_all_zwiftriders

    # Define constituents of one or more scenarios (4 pull speed scenarios in this case))

    dict_of_zwiftrideritem = get_all_zwiftriders()

    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    joshn : ZwiftRiderItem = dict_of_zwiftrideritem['joshn']
    richardm : ZwiftRiderItem = dict_of_zwiftrideritem['richardm']
    
    rider_scenario : list[ZwiftRiderItem] = [barryb, johnh, joshn, richardm]
    pull_duration_scenario = [30.0, 15.0, 10.0, 10.0]
    pull_speed_scenarios = [
        # [37.5, 37.5, 37.5, 37.5],
        # [40.0, 40.0, 40.0, 40.0],
        # [42.5, 42.5, 42.5, 42.5],
        [45.0, 44.0, 42.0, 37.0]
    ]

    # Compose the rider work_assignments, then work_efforts, then aggregate_efforts, and then stress_metrics for each scenario

    for i, scenario in enumerate(pull_speed_scenarios):

        work_assignments = compose_map_of_rider_work_assignments(rider_scenario, pull_duration_scenario, scenario)
        rider_efforts = populate_map_of_rider_efforts(work_assignments)
        rider_aggregate_efforts = calculate_rider_aggregate_efforts(rider_efforts)
        rider_stress_metrics = calculate_rider_stress_metrics(rider_aggregate_efforts)

        # display the results
        total_duration = next(iter(rider_aggregate_efforts.values())).total_duration
        average_speed = next(iter(rider_aggregate_efforts.values())).average_speed
        total_distance = next(iter(rider_aggregate_efforts.values())).total_distance
        table_heading= f"\nPull durations={pull_duration_scenario}sec\nPull speeds={pull_speed_scenarios[i]}km/h\nTotal_duration={total_duration}  Ave_speed={average_speed}  Total_dist={total_distance}"
        
        log_rider_aggregate_efforts(table_heading, rider_aggregate_efforts, logger)
        log_rider_stress_metrics(f"", rider_stress_metrics, logger)
        
if __name__ == "__main__":
    main()

