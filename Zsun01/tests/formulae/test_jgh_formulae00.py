from tabulate import tabulate
import time
import logging
from constants import COEFFICIENT_Cd, COEFFICIENT_Crr, COEFFICIENT_bike_weight_kg, AERO_POSITION_FACTOR_HOODS, AERO_POSITION_FACTOR_TT, AERO_POSITION_FACTOR_SUPERTUCK, AERO_POSITION_FACTOR_FULLTUCK
from jgh_formulae00 import demonstrateCdA, calculate_rolling_resistance_and_gravity_force, calculate_frontal_area,calculate_power_from_velocity, solve_for_velocity_from_power_using_binary_search
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING

def test00():
    aero_values : list[float] = [AERO_POSITION_FACTOR_HOODS, AERO_POSITION_FACTOR_TT, AERO_POSITION_FACTOR_SUPERTUCK, AERO_POSITION_FACTOR_FULLTUCK]
    height_values : list[float] = [155.0, 165.0, 175.0, 185.0, 195.0, 205.0]

    column_headers : list[str] = ["Height (cm)"] + [f"{m:.2f} aero factor" for m in aero_values]

    rows : list[str] = []
    for height in height_values:
        row : list[str] = [f"{height:.1f}"] # leftmost column in this row is  height
        for aero_factor in aero_values:
            area  = calculate_frontal_area(height_cm=height, aero_factor=aero_factor)
            row.append(f"{area:.2f}") 
        rows.append(row)

    print("Frontal area (m^2) as a function of height and aero-position.")
    print("     calculate_frontal_area()")
    print("Note: This is the frontal area, not the CdA. To get CdA, multiply frontal area by Cd (0.88) - see calculate_frontal_area()")
    print(f"aero values: hoods, tt, supertuck, fulltuck")
    print(tabulate(tabular_data = rows, headers=column_headers, tablefmt="rounded_outline"))
    print("\n")


def test01():
    aero_values : list[float] = [AERO_POSITION_FACTOR_HOODS, AERO_POSITION_FACTOR_TT, AERO_POSITION_FACTOR_SUPERTUCK, AERO_POSITION_FACTOR_FULLTUCK]
    height_values : list[float] = [155.0, 165.0, 175.0, 185.0, 195.0, 205.0]
    column_headers : list[str] = ["Height (cm)"] + [f"{m:.2f} aero factor" for m in aero_values]

    rows : list[str] = []
    for height in height_values:
        row : list[str] = [f"{height:.1f}"] # leftmost column in this row is  height
        for aero_factor in aero_values:
            cdA  = demonstrateCdA(height_cm=height, aero_position_factor=aero_factor)
            row.append(f"{cdA:.2f}") 
        rows.append(row)

    print("CdA (m^2) as a function of height and aero-position.")
    print("     demonstrateCdA()")
    print("Note: This is the CdA, not the frontal area.")
    print(f"aero values: hoods, tt, supertuck, fulltuck")
    print(tabulate(tabular_data = rows, headers=column_headers, tablefmt="rounded_outline"))
    print("\n")

def test02():
    rider_weight: float = 75.0  # kg
    mass: float = rider_weight + COEFFICIENT_bike_weight_kg

    mass_values : list[float] = [0.0, 60.0, 70.0, 80.0, 90.0, 100.0, 120.0]
    slope_values : list[float] = [-8.0, -4.0, 0.0, 4.0, 8.0]

    column_headers : list[str] = ["Slope %"] + [f"{m:.0f}kg" for m in mass_values]

    rows : list[str] = []
    for slope in slope_values:
        row : list[str] = [f"{slope:.1f}"] # leftmost column in this row is  slope
        for mass in mass_values:
            rr_N, fg_N  = calculate_rolling_resistance_and_gravity_force(mass_kg=mass, slope_pc=slope)
            row.append(f"{rr_N:.0f}" + " " f"{fg_N:.0f}") 
            # row.append(f"{rr_N + fg_N:.0f}") 
        rows.append(row)

    print("Forces (N) as a function of slope and mass.")
    print("     calculate_rolling_resistance_and_gravity_force()")
    print("Note: The first value is rolling resistance, the second value is gravity force.")

    print(tabulate(tabular_data = rows, headers=column_headers, tablefmt="rounded_outline"))
    print("\n")

def test03():
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
    print(f"    solve_for_velocity_from_power_using_binary_search()")
    print(f"In the hoods:")
    speed_kmh: float = solve_for_velocity_from_power_using_binary_search(power_watts=power_300, height_cm=height, total_mass_kg=total_mass, slope_pc=gradient, aero_factor=AERO_POSITION_FACTOR_HOODS)
    print(f"Speed: {speed_kmh:.2f} km/h at {power_300}W on gradient of {gradient}%  ZwiftInsider got 40.19 kph")
    speed_kmh: float = solve_for_velocity_from_power_using_binary_search(power_watts=power_400, height_cm=height, total_mass_kg=total_mass, slope_pc=gradient, aero_factor=AERO_POSITION_FACTOR_HOODS)
    print(f"Speed: {speed_kmh:.2f} km/h at {power_400}W on gradient of {gradient}%  ZwiftInsider got 44.53 kph")

    print(f"In the aero position:")
    speed_kmh: float = solve_for_velocity_from_power_using_binary_search(power_watts=power_300, height_cm=height, total_mass_kg=total_mass, slope_pc=gradient, aero_factor=AERO_POSITION_FACTOR_TT)
    print(f"Speed: {speed_kmh:.2f} km/h at {power_300}W on gradient of {gradient}%")
    speed_kmh: float = solve_for_velocity_from_power_using_binary_search(power_watts=power_400, height_cm=height, total_mass_kg=total_mass, slope_pc=gradient, aero_factor=AERO_POSITION_FACTOR_TT)
    print(f"Speed: {speed_kmh:.2f} km/h at {power_400}W on gradient of {gradient}%")

    print("\n")

def test04():
    rider_weight: float = 75.0  # kg
    height: float = 183
    mass: float = rider_weight + COEFFICIENT_bike_weight_kg

    velocity_values : list[float] = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]
    slope_values : list[float] = [0.0, 4.0, 5.0, 6.0, 7.0, 8.0]

    column_headers : list[str] = ["Slope %"] + [f"{z}kph" for z in velocity_values]

    rows : list[str] = []
    for slope in slope_values:
        row : list[str] = [f"{slope:.1f}"] # leftmost column is slope
        for velocity in velocity_values:
            power_w : float = calculate_power_from_velocity(velocity_kph=velocity, height_cm=height, total_mass_kg=mass, slope_pc=slope, aero_factor=AERO_POSITION_FACTOR_HOODS)
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
    mass: float = rider_weight + COEFFICIENT_bike_weight_kg

    power_values : list[float] = [0.0, 100.0, 150.0, 200.0, 300.0, 400.0]
    slope_values : list[float] = [-3.0, -4.0, -5.0, -6.0, -7.0, -8.0]

    column_headers : list[str] = ["Slope %"] + [f"{z}W" for z in power_values]

    rows : list[str] = []
    for slope in slope_values:
        row : list[str] = [f"{slope:.1f}"] # leftmost column is slope
        for power in power_values:
            speed_kmh : float = solve_for_velocity_from_power_using_binary_search(power_watts=power, height_cm=height, total_mass_kg=mass, slope_pc=slope, aero_factor=AERO_POSITION_FACTOR_SUPERTUCK)
            row.append(f"{speed_kmh:.0f}") 
        rows.append(row)
    print(f"Descending speed for {rider_weight} kg rider in supertuck position.")
    print(f"        solve_for_velocity_from_power_using_binary_search()")   
    print(f"Cipressa = 3.5%, Alto de Patios = 6.0%,The Grade KOM = 8.6%, Alpe du Zwift = 8.5%,")   
    print(tabulate(tabular_data = rows, headers=column_headers, tablefmt="rounded_outline"))
    print("\n")

#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        test01()
        test02()
        test03()
        test04()
        test05()

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



