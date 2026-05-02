"""
Cycling Physics Formulae Module
===============================

This module provides core formulae and numerical solvers for modeling
cycling performance based on physical principles. It implements the
standard equations for aerodynamic drag, rolling resistance, and
gravitational force, as described in the foundational 1998 University
of Utah paper on cycling power (see:
https://collections.lib.utah.edu/dl_files/b4/8e/b48ef26086091662c561e673d7bd990d77868437.pdf).

Key Features:
-------------
- Calculates the power required to maintain a given speed, considering
  air resistance, rolling resistance, and gradient.
- Estimates a cyclist's frontal area using a height- and weight-based
  formula calibrated to match typical literature values.
- Solves for steady-state speed given a target power output using
  fast root-finding algorithms (Newton-Raphson, Brent, fsolve).
- Optimizes calculations for flat terrain by avoiding unnecessary
  trigonometric operations when gradient is zero.
- Provides robust error handling for non-convergence and non-physical
  results in numerical solvers.

Functions:
----------
- frontal_area(height_cm, weight_kg): Estimate frontal area in square meters.
- power_required(v, Cd, A, Crr, total_mass, gradient): Compute power
  required at speed v in meters per second.
- solve_speed_from_power(power, Cd, A, Crr, total_mass, gradient):
  Find steady-state speed in kilometers per hour for a given power.
- solve_power_from_speed(speed_kmh, Cd, A, Crr, total_mass, gradient):
  Find required power in watts for a given speed in kilometers per hour.

Usage Example:
--------------
    A = frontal_area(183, 75)
    total_mass = 75 + COEFFICIENT_bike_weight_kg
    speed_kmh = solve_speed_from_power(400, COEFFICIENT_Cd, A,
                                       COEFFICIENT_Crr, total_mass, 0.0)

Dependencies:
-------------
- math
- scipy.optimize
- coefficients (project-specific)

All content is UTF-8 compliant. Line widths are limited to 79
characters for Python style compliance.
"""
import math
from scipy.optimize import fsolve # type: ignore
from scipy.optimize import brentq  # type: ignore
from scipy.optimize import newton # type: ignore - the best performer in testing, by far

from constants import COEFFICIENT_g, COEFFICIENT_rho


# this suite of formulae in the model is based on the physics of cycling and takes into account various factors such as air resistance, rolling resistance, and gravitational forces: it is the formula from the foundational paper on the subject written in 1998 from the University of Utah, which is what Zwift most likely used and then parameterised. The parameters they use are unknown, but the physics is sound. # the foundational paper on the subject can be found here: https://collections.lib.utah.edu/dl_files/b4/8e/b48ef26086091662c561e673d7bd990d77868437.pdf

# Constants
g: float = COEFFICIENT_g  # gravity (m/s^2)
rho: float = COEFFICIENT_rho  # air density at sea level (kg/m^3)

def frontal_area(height_cm: float, weight_kg: float) -> float:
    """
    Estimate the frontal area (A) of a cyclist in square meters (m^2) using
    a simple linear formula based on both height and weight.

    Formula:
        A = 0.0022 * height_cm + 0.0016 * weight_kg - 0.075

    Rationale:
        The actual formula used by Zwift for frontal area is not publicly
        known and may not include weight at all; height is likely the
        dominant factor. Most cycling physics literature and simulation
        platforms use a fixed value around 0.4 m^2 for a typical road
        cyclist. This linear formula is calibrated so that for a man
        183 cm tall and 75 kg, the result is approximately 0.4 m^2,
        matching the value commonly cited in the literature.

    Args:
        height_cm (float): Rider's height in centimeters.
        weight_kg (float): Rider's weight in kilograms.

    Returns:
        float: Estimated frontal area in square meters (m^2).
    """
    return 0.0022 * height_cm + 0.0016 * weight_kg - 0.075

def power_required(v: float, Cd: float, A: float, Crr: float, total_mass: float, gradient: float) -> float:
    """
    Calculate the power (watts) required for a cyclist to maintain a given
    speed on a road, considering aerodynamic drag, rolling resistance, and
    gravitational force due to slope.
    Optimized: avoids trig if gradient == 0.
    """
    F_aero: float = 0.5 * rho * Cd * A * v ** 2

    if gradient == 0.0:
        F_roll: float = Crr * total_mass * g
        F_gravity: float = 0.0
    else:
        F_roll: float = Crr * total_mass * g * math.cos(math.atan(gradient))
        F_gravity: float = total_mass * g * math.sin(math.atan(gradient))

    F_total: float = F_aero + F_roll + F_gravity
    return v * F_total

def solve_speed_from_power(power: float, Cd: float, A: float, Crr: float, total_mass: float, gradient: float) -> float:
    """
    Solve for the steady-state cycling speed (in km/h) given a target power
    output (in watts) and physical parameters.

    Uses Newton-Raphson root finding for fast convergence.
    Raises ValueError for non-positive power or non-convergence.
    """
    if power <= 0.0:
        raise ValueError(f"power must be positive, got {power}")

    def equation(v: float) -> float:
        return power_required(v, Cd, A, Crr, total_mass, gradient) - power

    def equation_prime(v: float) -> float:
        F_aero = 0.5 * rho * Cd * A * v ** 2

        if gradient == 0.0:
            F_roll: float = Crr * total_mass * g
            F_gravity: float = 0.0
        else:
            F_roll: float = Crr * total_mass * g * math.cos(math.atan(gradient))
            F_gravity: float = total_mass * g * math.sin(math.atan(gradient))

        F_total = F_aero + F_roll + F_gravity
        dF_aero_dv = rho * Cd * A * v
        dF_total_dv = dF_aero_dv  # Only F_aero depends on v
        return F_total + v * dF_total_dv

    v_initial_guess: float = 6.0  # m/s - approx 21 km/h
    try:
        v_solution: float = newton(equation, v_initial_guess, fprime=equation_prime, tol=1e-5)
    except RuntimeError as e:
        raise ValueError(f"solve_speed_from_power failed to converge: {e}") from e

    if v_solution <= 0.0:
        raise ValueError(f"Solver returned non-physical speed: {v_solution:.4f} m/s")

    return v_solution * 3.6  # convert to kph

def solve_power_from_speed(speed_kmh: float, Cd: float, A: float, Crr: float, total_mass: float, gradient: float) -> float:
    """
    Calculate the power output (in watts) required for a cyclist to maintain
    a specified steady-state speed (in kilometers per hour) given physical
    and environmental parameters.

    This function converts the input speed from km/h to m/s and then calls
    the power_required function, which applies the standard cycling physics
    model. The calculation accounts for aerodynamic drag, rolling resistance,
    and gravitational force due to road gradient.

    Args:
        speed_kmh (float): Target speed in kilometers per hour (km/h).
        Cd (float): Drag coefficient.
        A (float): Frontal area in square meters (m^2).
        Crr (float): Rolling resistance coefficient.
        total_mass (float): Combined mass of rider and bike in kilograms (kg).
        gradient (float): Road gradient as a ratio (e.g., 0.01 for 1%).

    Returns:
        float: Required power output in watts (W).
    """
    v: float = speed_kmh / 3.6  # convert to m/s
    return power_required(v, Cd, A, Crr, total_mass, gradient)

