import math


from constants import AERO_POSITION_FACTOR_HOODS, SINGLE_RIDER_ROUTE_NAME
from jgh_formulae01 import calculate_rider_kph_from_watts
from repository_of_routes import RepositoryOfRoutes

from jgh_number import safe_divide
from jgh_string import cleanup_name_string, format_seconds_to_hh_mm_ss


import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


def test00():
    # ZwiftInsider https://zwiftinsider.com/tt-drafting-pd41/ and https://zwiftinsider.com/road-bike-drafting-pd41/ 
    rider_weight_kg: float = 75.0  # kg 
    height_cm: float = 183
    power: float = 300.0  # on a road bike the speed should be 40.19 kph (TT bike 41.83 kph)
    # power: float = 400.0  # on a road bike the speed should be 44.53 kph (TT bike 46.47 kph )

    # for TTT, ZwiftInsider rode bog standard Zwift TT frame with Zipp 808 wheels (weight is a Zwift secret)
    # for road, ZwiftInsider rode bog standard Zwift Carbon road bike frames with Zwift 32mm carbon wheels (weight is a Zwift secret)

    speed_kmh: float = calculate_rider_kph_from_watts(power, rider_weight_kg, height_cm, 0.0, AERO_POSITION_FACTOR_HOODS)

    print(f"Estimated speed: {speed_kmh:.2f} km/h at {power}W on a gradient of 0.0%")

def test01():
    rider_weight_kg: float = 77.0  # jgh 77, kevin 75
    height_cm: float = 178 # jgh 171, kevin 178
    power_watts: float = 120.0 # 186W is Jgh threshold power for this route. Kevin did it on Rouvy at 161W
    routeItem = RepositoryOfRoutes.get_RouteItem(SINGLE_RIDER_ROUTE_NAME)

    for bucket in routeItem.route_slope_buckets:
        speed_kph = calculate_rider_kph_from_watts(power_watts,rider_weight_kg, height_cm, bucket.bucket_slope_pc, AERO_POSITION_FACTOR_HOODS)
        bucket.calculated_bucket_watts = round(power_watts, 1)
        if speed_kph <= 0:
            bucket.calculated_bucket_speed_kph = 0.0
            bucket.calculated_bucket_duration_sec = float('inf')
        else:
            duration_sec = (bucket.bucket_length_km * 1000.0) / (speed_kph / 3.6)
            bucket.calculated_bucket_duration_sec = round(duration_sec, 1)
            bucket.calculated_bucket_speed_kph = round(speed_kph, 2)

    route_time_sec = sum(bucket.calculated_bucket_duration_sec for bucket in routeItem.route_slope_buckets)

    if not math.isfinite(route_time_sec):
        route_hh_mm_ss = "n/a"
    else:
        route_hh_mm_ss = format_seconds_to_hh_mm_ss(route_time_sec)

    route_wkg = round(safe_divide(power_watts, rider_weight_kg), 2)
    route_kph = round(safe_divide(routeItem.route_lead_in_km + routeItem.route_length_km, route_time_sec/3600.0), 1)
    route_av_gradient = round (safe_divide(routeItem.route_elevation_m, routeItem.route_length_km*1000.0)*100.0, 1) 

    print(f"Route: {routeItem.route_name}, {routeItem.route_length_km} km, {routeItem.route_elevation_m} m, {route_av_gradient}%\nTime: {route_hh_mm_ss} at {route_kph:.2f} km/h for {power_watts}W ({route_wkg:.2f} W/kg)")


#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        # test00()
        test01()

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.\n")

    except AlertMessageError as alert_err:
        log_event(
            logger,
            message=alert_err.message,
            level=logging.INFO,
            exception=alert_err
        )
        print(f"{alert_err.message}\n")

    except Exception as ex:
        log_event(
            logger,
            message=f"Unhandled Exception: {ex}",
            level=logging.ERROR,
            exception=ex  # Pass the original exception object
        )
        print(f"Unhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n")



