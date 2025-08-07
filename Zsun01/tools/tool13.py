"""
This tool analyzes and optimizes paceline strategies for a specified team of riders, focusing on pull speed bounds and rotation schedules.

The script performs the following steps:
- Configures logging for the application.
- Loads rider data for a specified team and arranges riders in an optimal order for paceline efficiency.
- Calculates upper and lower bounds for paceline pull speeds using both maximum and one-hour power metrics, logging the results.
- Generates a simple paceline plan using equal pull durations and evaluates it for exertion constraints.
- Enumerates all possible pull period rotation schedules within defined standard pull periods.
- Searches for optimal paceline solutions using a parallelized work-stealing algorithm, considering exertion constraints and speed.
- Logs detailed rider contributions for the simplest, most balanced, and highest-speed paceline plans.
- Summarizes the computational effort, including the number of alternatives evaluated and total compute time.

This tool demonstrates advanced team time trial (TTT) strategy modeling, combinatorial optimization, and performance analytics for cycling using Python.
"""

from zsun_rider_item import ZsunItem
from jgh_number import safe_divide
from handy_utilities import read_json_dict_of_ZsunDTO
from jgh_formulae02 import calculate_lower_bound_paceline_speed, calculate_lower_bound_paceline_speed_at_one_hour_watts, calculate_upper_bound_paceline_speed, calculate_upper_bound_paceline_speed_at_one_hour_watts
from jgh_formulae02 import arrange_riders_in_optimal_order
from jgh_formulae06 import log_rider_contributions
from jgh_formatting import format_number_with_comma_separators, format_pretty_duration_hms, truncate 
from jgh_formulae08 import generate_all_paceline_rotation_sequences_in_the_total_solution_space
from jgh_formulae08 import generate_a_single_paceline_solution_complying_with_exertion_constraints, generate_paceline_solutions_using_parallel_workstealing_algorithm
from constants import STANDARD_PULL_PERIODS_SEC_AS_LIST, EXERTION_INTENSITY_FACTOR_LIMIT
from filenames import RIDERS_FILE_NAME
from dirpaths import DATA_DIRPATH
from repository_of_team_rosters import get_riderIDs_on_team_roster
import logging
logger = logging.getLogger(__name__)

def main():

    dict_of_ZsunItems = read_json_dict_of_ZsunDTO(RIDERS_FILE_NAME, DATA_DIRPATH)
    riderIDs = get_riderIDs_on_team_roster("test")
    riders: list[ZsunItem] = [dict_of_ZsunItems[riderID] for riderID in riderIDs]
    riders = arrange_riders_in_optimal_order(riders)

    logger.info(f"\nPACELINE PULL SPEED: upper and lower bounds: -\n")

    r01, r01_duration, r01_speed = calculate_upper_bound_paceline_speed(riders)
    r02, _, r02_speed = calculate_upper_bound_paceline_speed_at_one_hour_watts(riders)
    logger.info(f"Upper bound pull        :  {round(r01_speed)} kph @ {round(r01.get_standard_30sec_pull_watts())} W ({round(safe_divide(r01.get_standard_30sec_pull_watts(), r01.weight_kg), 1)} W/kg) by {r01.name} for a pull of {round(r01_duration)} seconds.")
    logger.info(f"Upper bound 1-hour pull :  {round(r02_speed)} kph @ {round(r02.get_one_hour_watts())} W ({round(safe_divide(r02.get_one_hour_watts(), r02.weight_kg), 1)} W/kg) by {r02.name}.")

    r01, r01_duration, r01_speed = calculate_lower_bound_paceline_speed(riders)
    r02, _, r02_speed = calculate_lower_bound_paceline_speed_at_one_hour_watts(riders)
    logger.info(f"Lower bound pull        :  {round(r01_speed)} kph @ {round(r01.get_standard_4_minute_pull_watts())} W ({round(safe_divide(r01.get_standard_4_minute_pull_watts(), r01.get_one_hour_watts()), 1)} W/kg) by {r01.name} for a pull of {round(r01_duration)} seconds.")
    logger.info(f"Lower bound 1-hour pull :  {round(r02_speed)} kph @ {round(r02.get_one_hour_watts())} W ({round(safe_divide(r02.get_one_hour_watts(), r02.weight_kg), 1)} W/kg) by {r02.name}.")

    lowest_bound_speed = round(min(truncate(r01_speed, 0), truncate(r02_speed, 0), 1))  # round to lowest 1 kph, as a float
    simplest_pull_durations = [60.0] * len(riders)  # seed: 60 seconds for everyone for Simplest case to execute as a team
    lowest_bound_speed_as_array = [lowest_bound_speed] * len(riders)

    from computation_classes import PacelineIngredientsItem

    # Prepare params for single plan
    simple_params = PacelineIngredientsItem(
        riders_list                     =riders,
        sequence_of_pull_periods_sec    =simplest_pull_durations,
        pull_speeds_kph                 =lowest_bound_speed_as_array,
        max_exertion_intensity_factor   =EXERTION_INTENSITY_FACTOR_LIMIT
    )
    simple_result = generate_a_single_paceline_solution_complying_with_exertion_constraints(simple_params)
    simple_plan_line_items = simple_result.rider_contributions

    all_conceivable_paceline_rotation_schedules = generate_all_paceline_rotation_sequences_in_the_total_solution_space(len(riders), STANDARD_PULL_PERIODS_SEC_AS_LIST)

    # Prepare params for optimal search
    standard_params = PacelineIngredientsItem(
        riders_list                     =riders,
        sequence_of_pull_periods_sec    =STANDARD_PULL_PERIODS_SEC_AS_LIST,
        pull_speeds_kph                 =[lowest_bound_speed] * len(riders),
        max_exertion_intensity_factor   =EXERTION_INTENSITY_FACTOR_LIMIT
    )

    list_of_paceline_computation_reportitem = generate_paceline_solutions_using_parallel_workstealing_algorithm(
        standard_params, all_conceivable_paceline_rotation_schedules)

    for item in list_of_paceline_computation_reportitem:
        if not item.algorithm_ran_to_completion:
            logger.warning(f"Solution not found for parameters: {asdict(item)}")
        else:
            plan_guid = item.guid
            speed = round(item.calculated_average_speed_of_paceline_kph,2)
            iterations = item.compute_iterations_performed_count
            intensity_constraint = round(item.exertion_intensity_constraint_used, 2)
            std_dev_intensity = item.calculated_dispersion_of_intensity_of_effort

            logger.info(f"\nPlan GUID: {plan_guid} - Speed: {speed} kph, Iterations: {format_number_with_comma_separators(iterations)}, Intensity Constraint: {intensity_constraint}, Std Dev Intensity: {std_dev_intensity}")

    logger.info(f"\n\n\nReport: did {format_number_with_comma_separators(total_iterations)} iterations to evaluate {format_number_with_comma_separators(all_conceivable_paceline_rotation_schedules)} alternatives in {format_pretty_duration_hms(compute_time)} \n\n")

if __name__ == "__main__":
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logging.getLogger("numba").setLevel(logging.ERROR) # numba is noisy at INFO level

    main()


