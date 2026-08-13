from tabulate import tabulate
import time
import logging
from constants import COEFFICIENT_bike_weight_kg, AERO_POSITION_FACTOR_HOODS, AERO_POSITION_FACTOR_TT, AERO_POSITION_FACTOR_SUPERTUCK, AERO_POSITION_FACTOR_FULLTUCK
from jgh_formulae00 import calculate_CdA, calculate_rolling_resistance_and_gravity_force, calculate_frontal_area,calculate_power_from_velocity, calculate_velocity_from_power
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING

def test00():
    # ZwiftInsider https://zwiftinsider.com/tt-drafting-pd41/ and https://zwiftinsider.com/road-bike-drafting-pd41/ 
    # for TTT, ZwiftInsider rode bog standard Zwift TT frame with Zipp 808 wheels (weight is a Zwift secret)
    # for road, ZwiftInsider rode bog standard Zwift Carbon road bike frames with Zwift 32mm carbon wheels (weight is a Zwift secret)

    gradient: float = 0.00  # he rode on the dead flat, peumably in a normal position on the hoods
    rider_weight: float = 75.0  # kg 
    height: float = 183
    power_300: float = 300.0  # on a road bike he should be able to achieve 40.19 kph (TT bike 41.83 kph)
    power_400: float = 400.0  # on a road bike he should be able to achieve 44.53 kph (TT bike 46.47 kph )

    total_mass: float = rider_weight + COEFFICIENT_bike_weight_kg


    print(f"Benchmark vs ZwiftInsider's empirical measurements in the hoods on the flat.")
    print(f"    calculate_velocity_from_power()")
    print(f"In the hoods:")
    speed_kmh: float = calculate_velocity_from_power(power_300, height, total_mass, gradient, AERO_POSITION_FACTOR_HOODS)
    print(f"Speed: {speed_kmh:.2f} km/h at {power_300}W on gradient of {gradient}%  ZwiftInsider got 40.19 kph")
    speed_kmh: float = calculate_velocity_from_power(power_400, height, total_mass, gradient, AERO_POSITION_FACTOR_HOODS)
    print(f"Speed: {speed_kmh:.2f} km/h at {power_400}W on gradient of {gradient}%  ZwiftInsider got 44.53 kph")

    print(f"In the TT position:")
    speed_kmh: float = calculate_velocity_from_power(power_300, height, total_mass, gradient, AERO_POSITION_FACTOR_TT)
    print(f"Speed: {speed_kmh:.2f} km/h at {power_300}W on gradient of {gradient}%")
    speed_kmh: float = calculate_velocity_from_power(power_400, height, total_mass, gradient, AERO_POSITION_FACTOR_TT)
    print(f"Speed: {speed_kmh:.2f} km/h at {power_400}W on gradient of {gradient}%")

    print("\n")

def test01():
    aero_values : list[float] = [AERO_POSITION_FACTOR_HOODS, AERO_POSITION_FACTOR_TT, AERO_POSITION_FACTOR_SUPERTUCK, AERO_POSITION_FACTOR_FULLTUCK]
    height_values : list[float] = [155.0, 165.0, 175.0, 185.0, 195.0, 205.0]
    column_headers : list[str] = ["Height (cm)"] + [f"{m:.2f} aero factor" for m in aero_values]

    rows : list[str] = []
    for height in height_values:
        row : list[str] = [f"{height:.1f}"] # leftmost column in this row is  height
        for aero_factor in aero_values:
            cdA  = calculate_CdA(height, aero_factor)
            row.append(f"{cdA:.2f}") 
        rows.append(row)

    print("CdA (m^2) as a function of height and aero-position.")
    print("     calculate_CdA()")
    print("Note: This is the CdA, not the frontal area.")
    print(f"aero values: hoods, tt, supertuck, fulltuck")
    print(tabulate(tabular_data = rows, headers=column_headers, tablefmt="rounded_outline"))
    print("In June 2026, the GCN boys raced having achieved a CdA of 0.23 in the 'breakaway' position in full aero clothing. (which is not as good as the TT positon.) They")
    print("\n")

def test02():
    total_mass_values : list[float] = [0.0, 60.0, 70.0, 80.0, 90.0, 100.0, 120.0]
    slope_values : list[float] = [-8.0, -4.0, 0.0, 4.0, 8.0]

    column_headers : list[str] = ["Slope %"] + [f"{m:.0f}kg" for m in total_mass_values]

    rows : list[str] = []
    for slope in slope_values:
        row : list[str] = [f"{slope:.1f}"] # leftmost column in this row is  slope
        for total_mass in total_mass_values:
            rr_N, fg_N  = calculate_rolling_resistance_and_gravity_force(total_mass, slope)
            row.append(f"{rr_N:.0f}" + " " f"{fg_N:.0f}") 
            # row.append(f"{rr_N + fg_N:.0f}") 
        rows.append(row)

    print("Forces (N) as a function of slope and total_mass.")
    print("     calculate_rolling_resistance_and_gravity_force()")
    print("Note: The first value is rolling resistance, the second value is gravity force.")

    print(tabulate(tabular_data = rows, headers=column_headers, tablefmt="rounded_outline"))
    print("\n")

def test03():
    aero_values : list[float] = [AERO_POSITION_FACTOR_HOODS, AERO_POSITION_FACTOR_TT, AERO_POSITION_FACTOR_SUPERTUCK, AERO_POSITION_FACTOR_FULLTUCK]
    height_values : list[float] = [155.0, 165.0, 175.0, 185.0, 195.0, 205.0]

    column_headers : list[str] = ["Height (cm)"] + [f"{m:.2f} aero factor" for m in aero_values]

    rows : list[str] = []
    for height in height_values:
        row : list[str] = [f"{height:.1f}"] # leftmost column in this row is  height
        for aero_factor in aero_values:
            area  = calculate_frontal_area(height, aero_factor)
            row.append(f"{area:.2f}") 
        rows.append(row)

    print("Frontal area (m^2) as a function of height and aero-position.")
    print("     calculate_frontal_area()")
    print("Note: This is the frontal area, not the CdA. To get CdA, multiply frontal area by Cd (0.88) - see calculate_frontal_area()")
    print(f"aero values: hoods, tt, supertuck, fulltuck")
    print(tabulate(tabular_data = rows, headers=column_headers, tablefmt="rounded_outline"))
    print("\n")

def test04():
    rider_weight: float = 75.0  # kg
    height: float = 183
    total_mass: float = rider_weight + COEFFICIENT_bike_weight_kg

    velocity_values : list[float] = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]
    slope_values : list[float] = [0.0, 4.0, 5.0, 6.0, 7.0, 8.0]

    column_headers : list[str] = ["Slope %"] + [f"{z}kph" for z in velocity_values]

    rows : list[str] = []
    for slope in slope_values:
        row : list[str] = [f"{slope:.1f}"] # leftmost column is slope
        for velocity in velocity_values:
            power_w : float = calculate_power_from_velocity(velocity, height, total_mass, slope, AERO_POSITION_FACTOR_HOODS)
            row.append(f"{power_w:.0f}") 
        rows.append(row)
    print(f"Climbing power for {rider_weight} kg rider in the hoods.")
    print(f"        calculate_power_from_velocity()")
    print(f"Cipressa = 3.5%, Alto de Patios = 6.0%,The Grade KOM = 8.6%, Alpe du Zwift = 8.5%,")   
    print(tabulate(tabular_data = rows, headers=column_headers, tablefmt="rounded_outline"))
    print("\n")

def test05():
    rider_weight: float = 75.0  # kg
    height: float = 183
    total_mass: float = rider_weight + COEFFICIENT_bike_weight_kg

    power_values : list[float] = [0.0, 100.0, 150.0, 200.0, 300.0, 400.0]
    slope_values : list[float] = [-3.0, -4.0, -5.0, -6.0, -7.0, -8.0]

    column_headers : list[str] = ["Slope %"] + [f"{z}W" for z in power_values]

    rows : list[str] = []
    for slope in slope_values:
        row : list[str] = [f"{slope:.1f}"] # leftmost column is slope
        for power in power_values:
            speed_kmh : float = calculate_velocity_from_power(power, height, total_mass, slope, AERO_POSITION_FACTOR_SUPERTUCK)
            row.append(f"{speed_kmh:.0f}") 
        rows.append(row)
    print(f"Descending speed for {rider_weight} kg rider in supertuck position.")
    print(f"        calculate_velocity_from_power()")   
    print(f"Cipressa = 3.5%, Alto de Patios = 6.0%,The Grade KOM = 8.6%, Alpe du Zwift = 8.5%,")   
    print(tabulate(tabular_data = rows, headers=column_headers, tablefmt="rounded_outline"))
    print("\n")

#main runner
if __name__ == "__main__":
    import logging
    from jgh_exceptions import AlertMessageError
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        start_time = time.time()
        test01()
        test02()
        test03()
        # test04()
        # test05()
        end_time = time.time()

        success_msg = f"Success: Main execution completed successfully in {end_time - start_time:.2f} seconds."
        log_event(logger, message=success_msg, level=logging.INFO)
        print(f"\n{success_msg}\n")
    except AlertMessageError as alert_err:
        log_event(logger, message=alert_err.message, level=logging.INFO, exception=alert_err)
        print(f"{alert_err.message}\n")
    except Exception as ex:
        log_event(logger, message=f"Unhandled Exception: {ex}", level=logging.ERROR, exception=ex)  # Pass the original exception object
        print(f"Unhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n")


