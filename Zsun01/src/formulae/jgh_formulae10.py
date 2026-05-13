
def calculate_projected_accelerated_level_up(start_level: int, start_rider_score: int) -> int:
    """
    Calculate the projected end level using an accelerated levelling algorithm.
    Accelerated levelling up was launched end-April, 2026. ZwiftInsider explained
    everything in detail in this article: https://zwiftinsider.com/accelerated-leveling-101/

    The parameters must be the data for a rider as close as possible to D-Day of the launch. 
    JGH fortunately has a file of riders stats dated May 3rd and this is what we use.

    Note: in Zwift's JSON format, the rider score element is named "targetExperiencePoints".

    Starting from a given level and accumulated XP points, this function simulates
    level progression beyond level 100 by applying tiered XP decrements per level:
    - Levels 101-199: 15,000 XP per level
    - Levels 200-299: 15,750 XP per level
    - Levels 300+:    16,500 XP per level

    The baseline threshold is level 100 at 807,000 XP. The surplus XP above this
    threshold (adjusted for levels already gained) is used to project how many
    additional levels can be reached.

    Args:
        start_level (int): The current level to project from. Must be >= 100.
        start_points (int): The total accumulated XP points at the start level.

    Returns:
        int: The projected end level achievable with the given XP. Returns 0 if
             start_level is below 100.
    """

    if (start_level <100):
        return 0

    threshold_level : int = 100
    threshold_points : int = 807_000

    # print(f"ThresholdLevel = {threshold_level}, ThresholdPoints = {threshold_points}\n")

    points_decrement : int = 15_000
    # print(f"StartLevel = {start_level}, StartPoints = {start_points}\n")

    end_level : int = threshold_level
    points_surplus = start_rider_score - threshold_points - points_decrement*(start_level - threshold_level)
    # print(f"PointsSurplus = {points_surplus}\n")

    candidate_end_level :int = threshold_level
    candidate_end_points_surplus : int = points_surplus

    while candidate_end_points_surplus >= 0:
        candidate_end_level = end_level + 1

        if candidate_end_level <= 199:
            points_decrement = 15_000
        elif candidate_end_level <= 299:
            points_decrement = 15_750
        else:
            points_decrement = 16_500

        candidate_end_points_surplus = points_surplus - points_decrement
        # print(f"Level = {candidate_end_level}, PointsBalance = {candidate_end_points_surplus}, delta = {points_decrement}")

        if candidate_end_points_surplus >= 0:
            end_level = candidate_end_level
            points_surplus = candidate_end_points_surplus

    # print(f"EndLevel = {end_level}, EndPointsSurplus = {points_surplus}")

    return end_level

