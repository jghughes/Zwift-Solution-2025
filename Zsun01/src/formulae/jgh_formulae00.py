"""
Cycling Physics Formulae Module
================================

Academic Background and Literature
------------------------------------
The power model implemented here is drawn from the following peer-reviewed
literature. The physics is well-established and widely accepted.

1. Martin, J.C., Milliken, D.L., Cobb, J.E., McFadden, K.L., & Coggan,
   A.R. (1998). "Validation of a Mathematical Model for Road Cycling
   Power." Journal of Applied Biomechanics, 14(3), 276-291.
   https://collections.lib.utah.edu/dl_files/b4/8e/b48ef26086091662c561e673d7bd990d77868437.pdf

   This is the foundational paper for the entire power model. It
   validates the equation:

       P = v * (F_aero + F_roll + F_gravity)
         = v * (0.5*rho*CdA*v^2 + Crr*m*g*cos(theta) + m*g*sin(theta))

   where P is power (W), v is velocity (m/s), rho is air density (kg/m^3),
   CdA is the product of drag coefficient and frontal area (m^2), Crr is
   the rolling resistance coefficient, m is total mass (kg), g is
   gravitational acceleration (m/s^2), and theta is the road gradient
   angle (radians). Martin et al. treat CdA as a single empirically
   measured quantity rather than estimating A from anthropometric data.

2. Bassett, D.R., Kyle, C.R., Passfield, L., Broker, J.P., & Burke, E.R.
   (1999). "Comparing cycling world hour records, 1967-1996: modeling
   with empirical data." Medicine & Science in Sports & Exercise,
   31(11), 1665-1676. 
   
   Bassett et al. use a fixed frontal area of 
   approximately 0.4 m^2 for a standard road-cycling position. 
   Typical modern road positions are half this, highly dependent 
   on rider position.

3. Padilla, S., Mujika, I., Angulo, F., & Goiriena, J.J. (2000).
   "Scientific approach to the 1-h cycling world record." Journal of
   Applied Physiology, 89(4), 1522-1527.

   Padilla et al. used fixed empirical CdA values (e.g. 0.2294 m^2 in
   the time-trial position) derived from wind-tunnel measurements rather
   than anthropometric estimation. 
"""
import math

from constants import (
    COEFFICIENT_g, 
    COEFFICIENT_rho,
    COEFFICIENT_Cd,
    COEFFICIENT_Crr, 
    COEFFICIENT_bike_weight_kg,
    AERO_POSITION_FACTOR_DEFAULT,
    DEFAULT_PACELINE_SLOPE_PC,
    POWER_CURVE_IN_PACELINE,
)



def calculate_rolling_resistance_and_gravity_force(total_mass_kg: float, slope_pc: float) -> tuple[float, float]:
    """
    Return rolling resistance and gravity forces from total mass (kg) 
    and slope (%); returns (F_roll, F_gravity) in N.
    """
    theta : float = math.atan(slope_pc / 100.0)

    F_roll: float    = COEFFICIENT_Crr * total_mass_kg * COEFFICIENT_g * math.cos(theta) # always >= 0
    F_gravity: float = total_mass_kg * COEFFICIENT_g * math.sin(theta)        # <0 descent, >0 climb

    return F_roll, F_gravity


def calculate_frontal_area(height_cm: float, aero_factor: float = AERO_POSITION_FACTOR_DEFAULT) -> float:
    """
    Estimate frontal area from rider height (cm) and 
    aero factor (unitless); returns area (m^2).
    """
    answer = aero_factor * (0.00155 * height_cm) 

    return answer


def calculate_CdA(height_cm: float, aero_position_factor: float) -> float:
    """
    Estimate CdA from rider height (cm) and aero factor (unitless); returns CdA (m^2).
    """
    effective_frontal_area = calculate_frontal_area(height_cm, aero_position_factor)

    return COEFFICIENT_Cd * effective_frontal_area


def calculate_power_from_velocity(velocity_kph: float, height_cm: float, total_mass_kg: float, slope_pc: float, aero_factor: float = AERO_POSITION_FACTOR_DEFAULT) -> float:
    """
    Return required watts from speed (km/h), rider weight (kg), 
    rider height (cm), and slope (%); returns watts (W).
    """
    F_roll, F_gravity = calculate_rolling_resistance_and_gravity_force(total_mass_kg, slope_pc)

    velocity_mps: float = velocity_kph / 3.6  

    CdA = calculate_CdA(height_cm, aero_factor)
    F_aero: float = 0.5 * COEFFICIENT_rho * CdA * velocity_mps ** 2

    F_total: float = F_aero + F_roll + F_gravity

    power_w = F_total * velocity_mps

    if (power_w <= 0.0):
        return 0.0

    return power_w


def calculate_watts_from_speed(speed_kph: float, rider_weight_kg: float, rider_height_cm: float, slope_pc: float = DEFAULT_PACELINE_SLOPE_PC) -> float:
    """
    Calculate the power (watts) as a function of 
    speed (km/h), weight (kg), height (cm), slope (%).
    """

    rider_plus_bike_mass: float = rider_weight_kg + COEFFICIENT_bike_weight_kg
    watts = calculate_power_from_velocity(speed_kph, rider_height_cm, rider_plus_bike_mass, slope_pc)

    return watts


def calculate_drag_ratio_in_paceline(position_in_paceline: int) -> float:
    """
    Calculate the power factor based on the rider's position 
    in the paceline. The leader's factor is 1.0. Followers in 
    the paceline are based on ZwiftInsider's power matrix. 
    Their factors are less than 1.0, diminishing as they are 
    further back.This function guards against index out of 
    range errors if POWER_CURVE_IN_PACELINE is shorter than 8.
    """
    denominator = POWER_CURVE_IN_PACELINE[0]
    max_index = len(POWER_CURVE_IN_PACELINE) - 1
    # Clamp position to valid range (1 to len(POWER_CURVE_IN_PACELINE)), else use last available value
    if 1 <= position_in_paceline <= len(POWER_CURVE_IN_PACELINE):
        numerator = POWER_CURVE_IN_PACELINE[position_in_paceline - 1]
    else:
        numerator = POWER_CURVE_IN_PACELINE[max_index]  # Use last available value
    return numerator / denominator




