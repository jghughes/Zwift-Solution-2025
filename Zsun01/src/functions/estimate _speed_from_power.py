import math
# from scipy.optimize import fsolve

# this formula is based on the physics of cycling and takes into account various factors such as air resistance, rolling resistance, and gravitational forces: it is the formula from the foundational paper on the subject written in 1998 from the University of Utah, which is what zwift most likely used and then parameterised.

# the foundational paper on the subject can be found here: https://collections.lib.utah.edu/dl_files/b4/8e/b48ef26086091662c561e673d7bd990d77868437.pdf

# Constants
g: float = 9.80665  # gravity (m/s^2)
rho: float = 1.226  # air density at sea level (kg/m^3)

def frontal_area(height_cm: float, weight_kg: float) -> float:
    """Estimate frontal area A (m^2) from height and weight."""
    height_m: float = height_cm / 100
    return 0.2025 * (height_m ** 0.725) * (weight_kg ** 0.425)

def power_required(v: float, Cd: float, A: float, Crr: float, total_mass: float, gradient: float) -> float:
    """Calculate power required to maintain speed v (m/s)."""
    F_aero: float = 0.5 * rho * Cd * A * v ** 2
    F_roll: float = Crr * total_mass * g * math.cos(math.atan(gradient))
    F_gravity: float = total_mass * g * math.sin(math.atan(gradient))
    F_total: float = F_aero + F_roll + F_gravity
    return v * F_total

def solve_speed_from_power(power: float, Cd: float, A: float, Crr: float, total_mass: float, gradient: float) -> float:
    """Solve for speed (km/h) given power (watts)."""
    def equation(v: float) -> float:
        return power_required(v, Cd, A, Crr, total_mass, gradient) - power

    v_initial_guess: float = 5.0  # m/s
    v_solution: float = fsolve(equation, v_initial_guess)[0]
    return v_solution * 3.6  # convert to km/h

def solve_power_from_speed(speed_kmh: float, Cd: float, A: float, Crr: float, total_mass: float, gradient: float) -> float:
    """Solve for power (watts) given speed (km/h)."""
    v: float = speed_kmh / 3.6  # convert to m/s
    return power_required(v, Cd, A, Crr, total_mass, gradient)

# Example input
rider_weight: float = 70.0  # kg
bike_weight: float = 8.0  # kg
height_cm: float = 175.0
power: float = 250.0  # watts
Cd: float = 0.63  # typical for road cyclist
Crr: float = 0.004  # typical for road tires
gradient: float = 0.0  # flat road

# Calculations
A: float = frontal_area(height_cm, rider_weight)
total_mass: float = rider_weight + bike_weight
speed_kmh: float = solve_speed_from_power(power, Cd, A, Crr, total_mass, gradient)

print(f"Estimated speed: {speed_kmh:.2f} km/h at {power}W on flat terrain")
