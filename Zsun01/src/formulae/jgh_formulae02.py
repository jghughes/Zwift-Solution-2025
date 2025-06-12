from zsun_rider_item import ZsunRiderItem
from rolling_average import calculate_rolling_averages
from jgh_formulae01 import estimate_speed_from_wattage, estimate_watts_from_speed, estimate_drag_ratio_in_paceline
from computation_classes import RiderContributionItem, RiderExertionItem
from typing import List, Tuple,DefaultDict

def calculate_kph_riding_alone(rider : ZsunRiderItem, power: float) -> float:
    """
    Estimate the speed (km/h) given the power (wattage), weight_kg (kg), and 
    height_cm (cm) using the Newton-Raphson method.

    Args:
    power (float): The power in watts.

    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(power, rider.weight_kg, rider.height_cm)
    return speed_kph

def calculate_wattage_riding_alone(rider : ZsunRiderItem, speed: float) -> float:
    """
    Calculate the power (P) as a function of speed (km/h), weight_kg (kg), and 
    height_cm (cm).

    Args:
    speed (float): The speed in km/h.

    Returns:
    float: The calculated power in watts.
    """
    # Calculate the power using the estimate_watts_from_speed function
    power = estimate_watts_from_speed(speed, rider.weight_kg, rider.height_cm)
    return power

def calculate_wattage_riding_in_the_paceline(rider : ZsunRiderItem, speed: float, position: int
) -> float:
    """
    Calculate the wattage required for a rider given their speed and position 
    in the peloton.

    Args:
    rider (ZsunRiderItem): The rider object.
    speed (float): The speed in km/h.
    position (int): The position in the peloton.

    Returns:
    float: The required wattage in watts.
    """
    # Calculate the base power required for the given speed
    base_power = calculate_wattage_riding_alone(rider, speed)

    # Get the power factor based on the rider's position in the peloton
    power_factor = estimate_drag_ratio_in_paceline(position)

    # Adjust the power based on the power factor
    adjusted_power = base_power * power_factor

    return round(adjusted_power, 3)

def calculate_speed_riding_in_the_paceline(rider : ZsunRiderItem, power: float, position: int
) -> float:
    """
    Calculate the speed (km/h) for a rider given their power output (watts) 
    and position in the peloton.

    Args:
    power (float): The power output in watts.
    position (int): The position in the peloton.

    Returns:
    float: The estimated speed in km/h.
    """
    # Get the power factor based on the rider's position in the peloton
    power_factor = estimate_drag_ratio_in_paceline(position)

    # Adjust the power based on the power factor
    adjusted_watts = power / power_factor

    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(adjusted_watts, rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_30sec_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 30-second pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_30sec_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_1_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 1-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_1_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_2_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 2-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_2_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_3_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 3-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_3_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_4_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 4-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_4_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_n_second_watts(rider : ZsunRiderItem, seconds: float) -> float:
    """
    Calculate the speed (km/h) for a rider given their power output (watts) 
    for a specific duration in seconds.
    Args:
    seconds (float): The duration in seconds.
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_n_second_watts(seconds), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_one_hour_watts(rider : ZsunRiderItem) -> float: 
    """
    Calculate the speed (km/h) for a rider given their one-hour power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_one_hour_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_overall_average_watts(efforts: List[RiderExertionItem]) -> float:
    """
    Calculate the average power for a list of efforts.
    The average power is calculated as the total work done (in kilojoules) divided by 
    the total duration (in seconds). The function sums the kilojoules for each workload 
    item and divides by the total duration to obtain the average power.

    Args:
        efforts (List[RiderExertionItem]): The list of efforts.
    Returns:
        float: The average power.
    """
    if not efforts:
        return 0

    total_kilojoules = sum(item.kilojoules for item in efforts)
    total_duration = sum(item.duration for item in efforts)
    average_watts = 1_000 * total_kilojoules / total_duration if total_duration != 0 else 0
    return average_watts


def calculate_overall_normalized_watts(efforts: List[RiderExertionItem]) -> float:
    """
    Calculate the normalized power for a list of efforts.

    Normalized Power (NP) is a metric used to better quantify the physiological 
    demands of a workout compared to average power. It accounts for the variability 
    in power output and provides a more accurate representation of the effort 
    required. The calculation involves several steps:

    1. Create a list of instantaneous wattages for every second of the durations 
       of all efforts.
    2. Calculate the 30-second rolling average power.
    3. Raise the smoothed power values to the fourth power.
    4. Calculate the average of these values.
    5. Take the fourth root of the average.

    Args:
        efforts (List[RiderExertionItem]): The list of efforts. 
        Each item contains the wattage and duration for a specific segment of the 
        workout.

    Returns:
        float: The normalized power.

    Example:
        >>> efforts = [
        ...     RiderExertionItem(position=1, speed=35, duration=60, wattage=200, wattage_ftp_ratio=0.8, kilojoules=12000),
        ...     RiderExertionItem(position=2, speed=30, duration=30, wattage=180, wattage_ftp_ratio=0.72, kilojoules=5400)
        ... ]
        >>> calculate_overall_normalized_watts(efforts)
        192.0

    In this example, the normalized power is calculated for two efforts. 
    The first item has a duration of 60 seconds and a wattage of 200, and the 
    second item has a duration of 30 seconds and a wattage of 180. The function 
    computes the normalized power based on these values.
    """
    if not efforts:
        return 0

    # Create a list of instantaneous wattages for every second of the durations of all efforts
    instantaneous_wattages: List[float] = []
    for item in efforts:
        instantaneous_wattages.extend([item.wattage] * int(item.duration))

    # Calculate rolling average power - TrainingPeaks uses a 30-second rolling average
    # Our pulls are 30, 60, and 120 seconds long, so we'll use a (arbitrary) 5-second rolling average
    rolling_avg_power = calculate_rolling_averages(instantaneous_wattages, 5)

    # Raise the smoothed power values to the fourth power
    rolling_avg_power_4 = [p ** 4 for p in rolling_avg_power]

    # Calculate the average of these values
    mean_power_4 = sum(rolling_avg_power_4) / len(rolling_avg_power_4)

    # Take the fourth root of the average
    normalized_watts = mean_power_4 ** 0.25

    return normalized_watts

def calculate_overall_average_speed_of_paceline_kph(exertions: DefaultDict[ZsunRiderItem, List[RiderExertionItem]]) -> float:
    """
    Calculate the average speed (km/h) for the rider is the paceline to whom 
    this list of paceline efforts belong.

    The average speed is calculated as the total distance covered divided by the total duration.
    Each effort should have a speed (km/h) and a duration (seconds).

    Args:
        efforts (List[RiderExertionItem]): The list of efforts.

    Returns:
        float: The average speed in km/h.
    """
    if not exertions:
        return 0.0

    # arbitrarily get the first RiderExertionItem in the exertions dict
    efforts = next(iter(exertions.values()))

    total_distance_km = sum((item.speed_kph * item.duration) / 3600.0 for item in efforts)
    total_duration_sec = sum(item.duration for item in efforts)

    if total_duration_sec == 0:
        return 0.0

    average_speed_kph = total_distance_km / (total_duration_sec / 3600.0)

    return average_speed_kph



def calculate_overall_intensity_factor_of_rider_contribution(rider: ZsunRiderItem, rider_contribution: RiderContributionItem) -> float:
    """
    Calculate the intensity factor for a given rider and their contribution plan.

    The intensity factor is defined as the ratio of the normalized watts for a rider's planned effort
    to their one-hour power (FTP). This metric is used to assess how hard a rider is working relative
    to their sustainable threshold.

    Args:
        rider (ZsunRiderItem): The rider for whom the intensity factor is being calculated.
        rider_contribution (RiderContributionItem): The contribution plan containing normalized watts for the rider.

    Returns:
        float: The calculated intensity factor. Returns 0.0 if the rider's one-hour watts is zero.

    """

    if rider.get_one_hour_watts() == 0:
        return 0.0
    return rider_contribution.normalized_watts / rider.get_one_hour_watts()


def calculate_upper_bound_paceline_speed(riders: List[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    """
    Determines the maxima of permitted pull speed among all standard pull durations of all riders.
    For each rider and each permitted pull duration (30s, 60s, 120s, 180s, 240s), this function calculates the speed
    the rider goes at their permitted pull watts for that duration. It returns the rider, duration, and speed
    corresponding to the overall fastest speed found.
    Args:
        riders (list[ZsunRiderItem]): List of ZsunRiderItem objects representing the riders.
    Returns:
        Tuple[ZsunRiderItem, float, float]: A tuple containing:
            - The ZsunRiderItem with the highest speed,
            - The pull duration in seconds for which this maxima occurs,
            - The maxima speed in kph.
    """
    fastest_rider = riders[0]
    fastest_duration = 30.0  # arbitrary short
    highest_speed = 0.0  # Arbitrarily low speed
    duration_functions = [
        (30.0, calculate_speed_at_standard_30sec_pull_watts),
        (60.0, calculate_speed_at_standard_1_minute_pull_watts),
        (120.0, calculate_speed_at_standard_2_minute_pull_watts),
        (180.0, calculate_speed_at_standard_3_minute_pull_watts),
        (240.0, calculate_speed_at_standard_4_minute_pull_watts),
    ]
    for rider in riders:
        for duration, func in duration_functions:
            speed = func(rider)
            if speed > highest_speed:
                highest_speed = speed
                fastest_rider = rider
                fastest_duration = duration
    return fastest_rider, fastest_duration, highest_speed

def calculate_lower_bound_paceline_speed(riders: List[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    """
    Determines the minima permitted pull speed among all standard pull durations of all riders.

    For each rider and each permitted pull duration (30s, 60s, 120s, 180s, 240s), this function calculates the speed
    the rider goes at their permitted pull watts for that duration. It returns the rider, duration, and speed
    corresponding to the overall slowest speed found.

    Args:
        riders (list[ZsunRiderItem]): List of ZsunRiderItem objects representing the riders.

    Returns:
        Tuple[ZsunRiderItem, float, float]: A tuple containing:
            - The ZsunRiderItem with the lowest speed,
            - The pull duration in seconds for which this minima occurs,
            - The minima speed in kph.
    """
    slowest_rider = riders[0]
    slowest_duration = 30.0  # arbitrary short
    slowest_speed = 100.0  # Arbitrarily high speed

    duration_functions = [
        (30.0, calculate_speed_at_standard_30sec_pull_watts),
        (60.0, calculate_speed_at_standard_1_minute_pull_watts),
        (120.0, calculate_speed_at_standard_2_minute_pull_watts),
        (180.0, calculate_speed_at_standard_3_minute_pull_watts),
        (240.0, calculate_speed_at_standard_4_minute_pull_watts),
    ]

    for rider in riders:
        for duration, func in duration_functions:
            speed = func(rider)
            if speed < slowest_speed:
                slowest_speed = speed
                slowest_rider = rider
                slowest_duration = duration

    return slowest_rider, slowest_duration, slowest_speed

def calculate_lower_bound_paceline_speed_at_one_hour_watts(riders: List[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    # (rider, duration_sec, speed_kph)
    slowest_rider = riders[0]
    slowest_duration = 3600.0  # 1 hour in seconds
    slowest_speed = calculate_speed_at_one_hour_watts(slowest_rider)

    for rider in riders:
        speed = calculate_speed_at_one_hour_watts(rider)
        if speed < slowest_speed:
            slowest_speed = speed
            slowest_rider = rider
            # duration is always 1 hour for this function
            slowest_duration = 3600.0

    return slowest_rider, slowest_duration, slowest_speed

def calculate_upper_bound_paceline_speed_at_one_hour_watts(riders: List[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    # (rider, duration_sec, speed_kph)
    fastest_rider = riders[0]
    fastest_duration = 3600.0  # 1 hour in seconds
    highest_speed = calculate_speed_at_one_hour_watts(fastest_rider)
    for rider in riders:
        speed = calculate_speed_at_one_hour_watts(rider)
        if speed > highest_speed:
            highest_speed = speed
            fastest_rider = rider
            # duration is always 1 hour for this function
            fastest_duration = 3600.0
    return fastest_rider, fastest_duration, highest_speed






