from typing import Optional
import math
from jgh_formatting import get_current_utc_iso8601_timestamp, format_number_2dp, format_number_0dp_padded1, format_number_0dp_padded3, format_number_0dp_padded4
from jgh_formulae00 import calculate_frontal_area
from jgh_formulae02 import solve_for_fastest_achievable_time_by_rider_for_segment_using_newton , calculate_hypothetical_power_of_rider_at_given_speed, solve_for_fastest_achievable_time_by_rider_for_route_using_binary_search
from jgh_number import safe_divide
from jgh_string import cleanup_name_string, format_seconds_to_hh_mm_ss

from paceline_modelling_items import CurveFittingResultItem
from zwift_item import ZwiftItem
from zwiftracingapp_item import ZwiftRacingAppItem
from rider_compute_item import RiderComputeItem
from rider_stats_item import RiderStatsItem
from zwiftpower_flattened_90_day_watts_item import ZwiftPowerFlattened90dayWattsItem
from slope_bucket_item import SlopeBucketItem
from route_item import RouteItem



def construct_CurveFittingResultItem(zwift_id: str, coefficient_one_hour: float, exponent_one_hour: float, r_squared_one_hour: float, coefficient_pull_curve: float,
    exponent_pull_curve: float,
    r_squared_pull_best_fit: float,
    critical_power: float,
    anaerobic_work_capacity: float,
) -> CurveFittingResultItem:
    """
    Constructs and returns a fully populated CurveFittingResultItem for a single rider.

    This is the sole place in the codebase where a CurveFittingResultItem is instantiated.
    All inputs are required -- callers must not pass None for any parameter.
    Unit conversions and rounding are applied here so that callers pass raw model outputs.

    Args:
        zwift_id (str):
            Zwift ID of the rider.
        coefficient_one_hour (float):
            Coefficient from the 60-minute decay model curve fit.
        exponent_one_hour (float):
            Exponent from the 60-minute decay model curve fit.
        r_squared_one_hour (float):
            R-squared goodness-of-fit from the 60-minute decay model.
        coefficient_pull_curve (float):
            Coefficient from the TTT pull decay model curve fit.
        exponent_pull_curve (float):
            Exponent from the TTT pull decay model curve fit.
        r_squared_pull_best_fit (float):
            R-squared goodness-of-fit from the TTT pull decay model.
        critical_power (float):
            Raw critical power in watts from the CP/W-prime model.
        anaerobic_work_capacity (float):
            Raw anaerobic work capacity in joules from the CP/W-prime model.
            Converted to kilojoules internally.

    Returns:
        CurveFittingResultItem: A fully populated curve fitting result item.
    """

    return CurveFittingResultItem(
        zwift_id                    = zwift_id,
        sixty_min_curve_coefficient = coefficient_one_hour,
        sixty_min_curve_exponent    = exponent_one_hour,
        sixty_min_curve_r_squared   = r_squared_one_hour,
        TTT_pull_curve_coefficient  = coefficient_pull_curve,
        TTT_pull_curve_exponent     = exponent_pull_curve,
        TTT_pull_curve_r_squared    = r_squared_pull_best_fit,
        CP                          = round(critical_power),
        AWC                         = round((anaerobic_work_capacity / 1_000.0), 1),
        when_curves_fitted          = get_current_utc_iso8601_timestamp(),
    )


def construct_RiderComputeItem(zwiftItem: ZwiftItem, zwiftracingappItem: Optional[ZwiftRacingAppItem], jghcurveItem: CurveFittingResultItem,) -> RiderComputeItem:
    """
    Constructs and returns a fully populated RiderComputeItem for a single rider.

    This is the sole place in the codebase where a RiderComputeItem is instantiated.
    zwiftItem and jghcurveItem are required -- callers must not pass None for either.
    By definition, a RiderComputeItem only exists for riders who have curve fit data.
    zwiftracingappItem is accepted as Optional; if None it is replaced with a default
    empty instance so that the rest of the function can operate unconditionally.

    Args:
        zwiftItem (ZwiftItem):
            Core Zwift profile data. Required -- callers must not pass None.
        zwiftracingappItem (Optional[ZwiftRacingAppItem]):
            ZwiftRacingApp profile data. If None, a default ZwiftRacingAppItem() is used.
            Some racers will not have ZwiftRacingApp data.
        jghcurveItem (CurveFittingResultItem):
            Curve fitting result for the rider. Required -- callers must not pass None.

    Returns:
        RiderComputeItem: A fully populated rider riderCompute item.
    """

    if zwiftracingappItem is None:
        zwiftracingappItem = ZwiftRacingAppItem()  # proceed with default values, not deemed critical. some racers will not have zwiftracingapp data

    name = zwiftracingappItem.full_name or f"{zwiftItem.first_name} {zwiftItem.last_name}"

    return RiderComputeItem(
        zwift_id                         = zwiftItem.zwift_id,
        name                             = cleanup_name_string(name),
        weight_kg                        = round((zwiftItem.weight_grams or 0.0) / 1_000.0, 1),
        zwift_country_code3              = zwiftItem.country_code3,
        height_cm                        = round((zwiftItem.height_mm or 0.0) / 10.0),
        gender                           = "m" if zwiftItem.is_male else "f",
        age_years                        = zwiftItem.age_years,
        age_group                        = zwiftracingappItem.age_group,
        zwift_FTP_watts                  = round(zwiftItem.ftp_on_zwift),
        velo_zwiftpower_zFTP_watts       = round(zwiftracingappItem.zp_FTP),
        zwift_racing_score               = round(zwiftItem.competition_metrics.zwift_racing_score),
        zwift_cat_open                   = zwiftItem.competition_metrics.zwift_category_open,
        zwift_cat_women                  = zwiftItem.competition_metrics.zwift_category_women,
        velo_rating_30_days              = round(zwiftracingappItem.raceitem.racing_score_max30_obj.velo_rating),
        velo_cat_num_30_days             = zwiftracingappItem.raceitem.racing_score_max30_obj.mixed_things_obj.velo_cat_num,
        velo_cat_name_30_days            = zwiftracingappItem.raceitem.racing_score_max30_obj.mixed_things_obj.velo_cat_name,
        jgh_60_min_curve_coefficient     = jghcurveItem.sixty_min_curve_coefficient,
        jgh_60_min_curve_exponent        = jghcurveItem.sixty_min_curve_exponent,
        jgh_TTT_pull_curve_coefficient   = jghcurveItem.TTT_pull_curve_coefficient,
        jgh_TTT_pull_curve_exponent      = jghcurveItem.TTT_pull_curve_exponent,
        jgh_TTT_pull_curve_fit_r_squared = jghcurveItem.sixty_min_curve_r_squared,
        jgh_when_curves_fitted           = jghcurveItem.when_curves_fitted,
    )


def construct_RiderStatsItem(zwiftItem: ZwiftItem, zwiftracingappItem: Optional[ZwiftRacingAppItem], jghRiderComputeItem: Optional[RiderComputeItem], 
                             watts_90_day_item: Optional[ZwiftPowerFlattened90dayWattsItem], projected_accelerated_level: int,
                             single_segment: SlopeBucketItem, routeItem: RouteItem) -> RiderStatsItem:
    """
    Constructs and returns a fully populated RiderStatsItem for a single rider.

    This is the sole place in the codebase where a RiderStatsItem is instantiated.
    All four data sources are accepted as Optional; any that are None are silently
    replaced with a default empty instance so that the rest of the function can
    operate unconditionally on non-None values.

    The function performs the following steps in order:
        1. Resolves None inputs to safe defaults.
        2. Instantiates RiderStatsItem from zwiftItem, zwiftracingappItem, and jghRiderComputeItem.
        3. Computes derived fields: zwift_zftp_wkg, zwift_cat_label, and velo_cat_label.
        4. Populates all wkg/w power fields from watts_90_day_item.

    Args:
        zwiftItem (ZwiftItem):
            Core Zwift profile data. Required -- callers must not pass None.
        zwiftracingappItem (Optional[ZwiftRacingAppItem]):
            ZwiftRacingApp profile data. If None, a default ZwiftRacingAppItem() is used.
            Many riders will not have ZwiftRacingApp data.
        jghRiderComputeItem (Optional[RiderComputeItem]):
            Curve-fitted power data. If None, a default RiderComputeItem() is used.
            Many riders lack this because they have no ZwiftPower 90-day watts data.
        watts_90_day_item (Optional[ZwiftPowerFlattened90dayWattsItem]):
            ZwiftPower 90-day best-power data. If None, a default ZwiftPowerFlattened90dayWattsItem() is used.
            Many riders will not have this data.
        projected_accelerated_level (int):
            The rider's projected level under the accelerated levelling-up scheme.
            Set to 0 if the rider was not present in the launch-date snapshot file.
        single_segment (SlopeBucketItem):
            The segment used to calculate the duration and power over a single segment, if any.
        routeItem (RouteItem):
            The route item used to calculate route-specific statistics, if any.
    
    Returns:
        RiderStatsItem: A fully populated rider statistics item.
    """

    if zwiftracingappItem is None:
        zwiftracingappItem = ZwiftRacingAppItem()  # proceed with default values, not deemed critical. many/most riders will not have zwiftracingapp data

    if jghRiderComputeItem is None:
        jghRiderComputeItem = RiderComputeItem()  # proceed with empty values, not deemed critical for rider stats. many riders will not have riderCompute items because they are not curve fitted because they lack zwiftpower90daywatts data

    if watts_90_day_item is None:
        watts_90_day_item = ZwiftPowerFlattened90dayWattsItem()  # proceed with default values, not deemed critical. many riders will not have zwiftpower 90-day watts data

    name = zwiftracingappItem.full_name or f"{zwiftItem.first_name} {zwiftItem.last_name}"
    weight_kg = round((zwiftItem.weight_grams or 0.0) / 1_000.0, 1)

    riderStatsItem = RiderStatsItem(
        zwift_id                    =   zwiftItem.zwift_id,
        name                        =   cleanup_name_string(name),
        zwift_country_code3         =   zwiftItem.country_code3,
        age                         =   zwiftItem.age_years,
        height_cm                   =   round((zwiftItem.height_mm or 0.0) / 10.0),
        weight_kg                   =   weight_kg,
        gender_code                 =   "m" if zwiftItem.is_male else "f",
        cat_open                    =   zwiftItem.competition_metrics.zwift_category_open,
        cat_women                   =   zwiftItem.competition_metrics.zwift_category_women,
        achievement_level           =   int(zwiftItem.achievement_level / 100.0),
        total_distance_km           =   round((zwiftItem.total_distance_meters or 0.0) / 1_000.0, 1),
        total_experience_points     =   zwiftItem.total_experience_points,
        rider_score                 =   zwiftItem.target_experience_points,
        projected_accelerated_level =   projected_accelerated_level,
        zwift_racing_score          =   round(zwiftItem.competition_metrics.zwift_racing_score),
        zwift_ftp_w                 =   round(zwiftItem.ftp_on_zwift),
        zwift_zftp_w                =   round(zwiftracingappItem.zp_FTP),
        zwift_zftp_wkg              =   0.0,
        zwift_cat_label             =   "",
        velo_age_group              =   zwiftracingappItem.age_group,
        velo_cat_num_30_days        =   zwiftracingappItem.raceitem.racing_score_max30_obj.mixed_things_obj.velo_cat_num,
        velo_cat_name_30_days       =   zwiftracingappItem.raceitem.racing_score_max30_obj.mixed_things_obj.velo_cat_name,
        velo_rating_30_days         =   round(zwiftracingappItem.raceitem.racing_score_max30_obj.velo_rating, 0),
        velo_cat_label              =   "",
        wkg_05sec=0.0,
        wkg_15sec=0.0,
        wkg_30sec=0.0,
        wkg_01min=0.0,
        wkg_02min=0.0,
        wkg_03min=0.0,
        wkg_05min=0.0,
        wkg_10min=0.0,
        wkg_12min=0.0,
        wkg_15min=0.0,
        wkg_20min=0.0,
        wkg_30min=0.0,
        wkg_40min=0.0,
        wkg_60min_curvefit          =   round(jghRiderComputeItem.get_1_hour_curvefit_wkg(), 2),
        w_05sec=0.0,
        w_15sec=0.0,
        w_30sec=0.0,
        w_01min=0.0,
        w_02min=0.0,
        w_03min=0.0,
        w_05min=0.0,
        w_10min=0.0,
        w_12min=0.0,
        w_15min=0.0,
        w_20min=0.0,
        w_30min=0.0,
        w_40min=0.0,
        w_60min_curvefit            =   round(jghRiderComputeItem.get_1_hour_curvefit_watts(), 2),
        timestamp                   =   get_current_utc_iso8601_timestamp(),
    )

    riderStatsItem.zwift_zftp_wkg = safe_divide(zwiftracingappItem.zp_FTP, riderStatsItem.weight_kg)

    if riderStatsItem.cat_open == "":
        riderStatsItem.cat_open = "?"
        riderStatsItem.cat_women = "?"
    if riderStatsItem.cat_women == "":
        if riderStatsItem.gender_code != "m":
            riderStatsItem.cat_women = "?"

    cat_combo_text = (
        riderStatsItem.cat_open
        if riderStatsItem.gender_code == "m"
        else riderStatsItem.cat_open + "/" + riderStatsItem.cat_women
    )

    zftp_wkg_text           = f"{format_number_2dp(round(riderStatsItem.zwift_zftp_wkg, 2))}wkg"
    zwift_racing_score_text = f"{format_number_0dp_padded3(riderStatsItem.zwift_racing_score)}zrs"
    riderStatsItem.zwift_cat_label = f"{zftp_wkg_text} - {zwift_racing_score_text} - {cat_combo_text}"

    velo_cat_num_text = format_number_0dp_padded1(riderStatsItem.velo_cat_num_30_days)
    velo_rating_text  = format_number_0dp_padded4(riderStatsItem.velo_rating_30_days)

    riderStatsItem.velo_cat_label = (
        "# none"
        if riderStatsItem.velo_rating_30_days == 0
        else f"{velo_rating_text} {riderStatsItem.velo_cat_name_30_days} - {velo_cat_num_text}"
    )

    riderStatsItem = ZwiftPowerFlattened90dayWattsItem.populate_riderStatsItem_with_90dayWattsItem(
        riderStatsItem, watts_90_day_item, weight_kg
    )


    riderStatsItem.frontal_area_m2 = calculate_frontal_area(riderStatsItem.height_cm, riderStatsItem.weight_kg)
    riderStatsItem.single_segment_distance_km = round(single_segment.bucket_length_km, 1)                                                              
    riderStatsItem.single_segment_duration_sec = round(solve_for_fastest_achievable_time_by_rider_for_segment_using_newton(jghRiderComputeItem, single_segment), 1)
    riderStatsItem.single_segment_duration_hh_mm_ss = format_seconds_to_hh_mm_ss(riderStatsItem.single_segment_duration_sec)  
    speedKph = safe_divide((riderStatsItem.single_segment_distance_km * 1_000.0), riderStatsItem.single_segment_duration_sec) * 3.6
    riderStatsItem.single_segment_watts = round(calculate_hypothetical_power_of_rider_at_given_speed(jghRiderComputeItem, speedKph, single_segment.bucket_slope_pc), 1) 
    riderStatsItem.single_segment_wgk = round(safe_divide(riderStatsItem.single_segment_watts, riderStatsItem.weight_kg), 2)

    riderStatsItem.route_name = routeItem.route_name
    riderStatsItem.route_zwift_world_name = routeItem.zwift_world_name
    riderStatsItem.route_description = routeItem.route_description
    riderStatsItem.route_length_km = routeItem.route_length_km
    riderStatsItem.route_elevation_m = routeItem.route_elevation_m
    riderStatsItem.route_lead_in_length_km = routeItem.lead_in_length_km
    routeItem = solve_for_fastest_achievable_time_by_rider_for_route_using_binary_search(jghRiderComputeItem, routeItem)
    riderStatsItem.route_imposed_intensity_factor = routeItem.imposed_intensity_factor


    route_time_sec = sum(b.calculated_bucket_duration_sec for b in routeItem.route_slope_buckets)
    if not math.isfinite(route_time_sec):
        riderStatsItem.route_fastest_achievable_time_sec = 0.0
        riderStatsItem.route_fastest_achievable_time_hh_mm_ss = "n/a"
    else:
        riderStatsItem.route_fastest_achievable_time_sec = round(route_time_sec, 1)
        riderStatsItem.route_fastest_achievable_time_hh_mm_ss = format_seconds_to_hh_mm_ss(route_time_sec)

    riderStatsItem.route_power_output_watts = round((routeItem.route_slope_buckets[0].calculated_bucket_watts if len(routeItem.route_slope_buckets) > 0 else 0.0), 1)
    riderStatsItem.route_power_output_wkg = round(safe_divide(riderStatsItem.route_power_output_watts, riderStatsItem.weight_kg), 2)
    return riderStatsItem
