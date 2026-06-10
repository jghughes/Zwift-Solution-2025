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

def demonstrateCdA(height_cm: float, aero_position_factor: float) -> float:
    """
    Demonstrate the calculation of the frontal area (CdA) for a cyclist.

    Args:
        height_cm (float): Rider's height in centimeters.
        aero_position_factor (float): Multiplier based on rider's position.

    Returns:
        float: CdA in square meters (m^2).
    """
    effective_frontal_area = calculate_frontal_area(height_cm, aero_position_factor)

    return COEFFICIENT_Cd * effective_frontal_area


def calculate_rolling_resistance_and_gravity_force(total_mass_kg: float, slope_pc: float) -> tuple[float, float]:
    """
    Calculate the rolling resistance and gravitational forces.

    For negative slopes (descents):
      - sin_theta < 0  →  F_gravity < 0  (gravity assists motion)
      - cos_theta > 0  →  F_roll   > 0  (rolling resistance always opposes motion)

    Returns:
        tuple[float, float]: (F_roll, F_gravity)
            F_roll   is always >= 0, unit is Newtons (N)
            F_gravity is negative on descents, positive on climbs
            unit is Newtons (N)
    """

    theta : float = math.atan(slope_pc / 100.0)

    F_roll: float    = COEFFICIENT_Crr * total_mass_kg * COEFFICIENT_g * math.cos(theta) # always >= 0
    F_gravity: float = total_mass_kg * COEFFICIENT_g * math.sin(theta)        # <0 descent, >0 climb

    return F_roll, F_gravity


def calculate_frontal_area(height_cm: float, aero_factor: float = AERO_POSITION_FACTOR_DEFAULT) -> float:
    """
    Estimate the frontal area (A) of a cyclist in square meters (m^2) using
    a simple formula based on height and riding position multiplier from ChatGPT.
    
    Formula:
        A = aero_factor * (0.0155 * height_cm)/100 

    Rationale:
        The actual formula used by Zwift for frontal area is not publicly
        known.

    Args:
        height_cm (float): Rider's height in centimeters.
        aero_factor (float): Multiplier based on rider's position.
            Defaults to AERO_POSITION_FACTOR_DEFAULT, which represents 
            a typical time trial position (not hoods or supertuck).

    Returns:
        float: Frontal area in square meters (m^2).

    """

    answer = aero_factor * (0.00155 * height_cm) 

    return answer


def calculate_power_from_velocity(velocity_kph: float, height_cm: float, total_mass_kg: float, slope_pc: float, aero_factor: float = AERO_POSITION_FACTOR_DEFAULT) -> float:
    """
    Calculate the mechanical power (W) required for a cyclist to maintain
    a specified steady-state velocity, given physical and environmental
    parameters. Defaults to a typical time-trial position for the 
    aero factor, which is not the same as the hoods position 
    or the supertuck position.

    This function implements the full Martin et al. (1998) cycling physics model:

        P = v * (F_aero + F_roll + F_gravity)

    Args:
        velocity_kph (float):
            Steady-state velocity in kilometres per hour (km/h).
        Cd (float):
            Dimensionless aerodynamic drag coefficient. 
            Typical value for a road cyclist in the drops: ~0.63.
        height_cm (float):
            Rider height in centimetres (cm).
        Crr (float):
            Dimensionless rolling resistance coefficient. 
            Typical value for road tyres on tarmac: ~0.004.
        total_mass_kg (float):
            Combined mass of rider and bicycle.
        slope_pc (float):
            Road gradient as a % (rise / run).
            For example, 5.0 for a 5% climb, -5.0 for a 5% descent,
            0.0 for flat terrain. Zwift's physics model applies an 
            attenuation factor to descents, so the effective slope 
            is reduced on negative gradients.

    Returns:
        float: Required mechanical power in watts (W).
    """

    F_roll, F_gravity = calculate_rolling_resistance_and_gravity_force(total_mass_kg, slope_pc)

    velocity_mps: float = velocity_kph / 3.6  # convert km/h to m/s (1 km/h = 1/3.6 m/s)

    frontal_area = calculate_frontal_area(height_cm, aero_factor)
    F_aero: float = 0.5 * COEFFICIENT_rho * COEFFICIENT_Cd * frontal_area * velocity_mps ** 2

    F_total: float = F_aero + F_roll + F_gravity

    power_w = F_total * velocity_mps

    if (power_w <= 0.0):
        return 0.0

    return power_w


def calculate_watts_from_speed(speed: float, rider_weight: float, rider_height: float, slope_pc: float = DEFAULT_PACELINE_SLOPE_PC) -> float:
    """
    Calculate the power (watts) as a function of speed (km/h), weight (kg), height (cm), slope (%).
    """

    rider_plus_bike_mass: float = rider_weight + COEFFICIENT_bike_weight_kg
    watts = calculate_power_from_velocity(speed, rider_height, rider_plus_bike_mass, slope_pc)

    return watts

def calculate_drag_ratio_in_paceline(position: int) -> float:
    """
    Calculate the power factor based on the rider's position in the peloton.
    The leader's factor is 1.0. Follower's in the paceline are based on ZwiftInsider's
    power matrix. Their factors are less than 1.0, diminishing as they are further back.
    This function guards against index out of range errors if POWER_CURVE_IN_PACELINE is shorter than 8.
    """
    denominator = POWER_CURVE_IN_PACELINE[0]
    max_index = len(POWER_CURVE_IN_PACELINE) - 1
    # Clamp position to valid range (1 to len(POWER_CURVE_IN_PACELINE)), else use last available value
    if 1 <= position <= len(POWER_CURVE_IN_PACELINE):
        numerator = POWER_CURVE_IN_PACELINE[position - 1]
    else:
        numerator = POWER_CURVE_IN_PACELINE[max_index]  # Use last available value
    return numerator / denominator




