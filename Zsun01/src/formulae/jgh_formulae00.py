"""
Cycling Physics Formulae Module
================================

Academic Background and Literature
------------------------------------
The power model implemented here is drawn from the following peer-reviewed
literature. The physics is well-established and widely accepted in both
the academic sports-science community and in cycling simulation software
such as Zwift, Golden Cheetah, and WKO.

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
   This module follows the same physics but estimates A separately via
   a linear anthropometric formula (see calculate_frontal_area() below and note 3).

2. Bassett, D.R., Kyle, C.R., Passfield, L., Broker, J.P., & Burke, E.R.
   (1999). "Comparing cycling world hour records, 1967-1996: modeling
   with empirical data." Medicine & Science in Sports & Exercise,
   31(11), 1665-1676.

   Bassett et al. use a fixed frontal area of approximately 0.4 m^2 for
   a standard road-cycling position. Typical modern road positions 
   with are half this, highly dependent on rider position.

3. Heil, D.P. (2001). "Body mass scaling of projected frontal area in
   competitive cyclists." European Journal of Applied Physiology,
   85(3-4), 358-366.

   Heil derived regression equations relating frontal area to body mass
   and height using photographic measurements of competitive cyclists.
   His key finding was that body mass is the stronger predictor of
   frontal area than height, particularly in the drop/aero position.
   His best-fit power-law formula for the drop position is:

       A = 0.00267 * mass**0.604   (r^2 = 0.74)

   For a 75 kg rider this yields A ~= 0.394 m^2, closely matching the
   0.4 m^2 reference value. Heil's power-law formula would be a more rigorously
   validated single-variable alternative if a change were ever desired.
   (Note from JGH: this needs to be checked. I am dubious.)

4. Padilla, S., Mujika, I., Angulo, F., & Goiriena, J.J. (2000).
   "Scientific approach to the 1-h cycling world record." Journal of
   Applied Physiology, 89(4), 1522-1527.

   Padilla et al. used fixed empirical CdA values (e.g. 0.2294 m^2 in
   the time-trial position) derived from wind-tunnel measurements rather
   than anthropometric estimation. This illustrates the alternative
   approach of direct measurement, which is more accurate but not
   available in a simulation context such as Zwift where rider geometry
   cannot be measured directly.

5. I have no idea where ChatGPT got the linear formula used in this module
    but it seems to work. The biggest guy in the club has 0.5 m**2 and the 
    smallest girl has 0.28 m**2, and the formula gives reasonable estimates for both. 
"""


import math
import warnings

from constants import COEFFICIENT_g, COEFFICIENT_rho,COEFFICIENT_Cd,COEFFICIENT_Crr, UPPER_BOUND_HEIGHT_CLAMP_CM, LOWER_BOUND_HEIGHT_CLAMP_CM, UPPER_BOUND_WEIGHT_CLAMP_KG, LOWER_BOUND_WEIGHT_CLAMP_KG, LOWER_BOUND_FRONTAL_AREA_CLAMP, LOWER_BOUND_SLOPE_CLAMP_PC, UPPER_BOUND_SLOPE_CLAMP_PC , UPPER_BOUND_SPEED_CLAMP_KPH, LOWER_BOUND_SPEED_CLAMP_KPH, LOWER_BOUND_POWER_CLAMP_W, UPPER_BOUND_POWER_CLAMP_W, LOWER_BOUND_AERO_POSITION_FACTOR_CLAMP, UPPER_BOUND_AERO_POSITION_FACTOR_CLAMP, AERO_POSITION_FACTOR_HOODS, AERO_POSITION_FACTOR_TT, AERO_POSITION_FACTOR_SUPERTUCK

# abbreviations
g: float = COEFFICIENT_g  # gravity (m/s^2)
rho: float = COEFFICIENT_rho  # air density at sea level (kg/m^3)

def _clampWeight(total_mass_kg: float) -> float:
    if total_mass_kg < LOWER_BOUND_WEIGHT_CLAMP_KG:
        warnings.warn(
            f"Unusually low total_mass_kg={total_mass_kg!r}: must be between {LOWER_BOUND_WEIGHT_CLAMP_KG} and {UPPER_BOUND_WEIGHT_CLAMP_KG}kg."
            f"Clamping to {LOWER_BOUND_WEIGHT_CLAMP_KG} kg.",
            UserWarning,
            stacklevel=2,
        )
        return LOWER_BOUND_WEIGHT_CLAMP_KG
    if total_mass_kg > UPPER_BOUND_WEIGHT_CLAMP_KG:
        warnings.warn(
            f"Unusually heavy total_mass_kg={total_mass_kg!r}: must be between {LOWER_BOUND_WEIGHT_CLAMP_KG} and {UPPER_BOUND_WEIGHT_CLAMP_KG}kg."
            f"Clamping to {UPPER_BOUND_WEIGHT_CLAMP_KG} kg.",
            UserWarning,
            stacklevel=2,
        )
        return UPPER_BOUND_WEIGHT_CLAMP_KG
    return total_mass_kg

def _clampHeight(height_cm: float) -> float:
    if height_cm < LOWER_BOUND_HEIGHT_CLAMP_CM:
        warnings.warn(
            f"Unusually short height_cm={height_cm!r}: must be between {LOWER_BOUND_HEIGHT_CLAMP_CM} and {UPPER_BOUND_HEIGHT_CLAMP_CM}cm."
            f"Clamping to {LOWER_BOUND_HEIGHT_CLAMP_CM} cm.",
            UserWarning,
            stacklevel=2,
        )
        return LOWER_BOUND_HEIGHT_CLAMP_CM
    if height_cm > UPPER_BOUND_HEIGHT_CLAMP_CM:
        warnings.warn(
            f"Unusually tall height_cm={height_cm!r}: must be between {LOWER_BOUND_HEIGHT_CLAMP_CM} and {UPPER_BOUND_HEIGHT_CLAMP_CM}cm."
            f"Clamping to {UPPER_BOUND_HEIGHT_CLAMP_CM} cm.",
            UserWarning,
            stacklevel=2,
        )
        return UPPER_BOUND_HEIGHT_CLAMP_CM
    return height_cm

def _clampAeroMultiplier(AERO_MULTIPLIER: float) -> float:
    if AERO_MULTIPLIER < LOWER_BOUND_AERO_POSITION_FACTOR_CLAMP:
        warnings.warn(
            f"Unusually low AERO_MULTIPLIER={AERO_MULTIPLIER!r}: must be between {LOWER_BOUND_AERO_POSITION_FACTOR_CLAMP} and {UPPER_BOUND_AERO_POSITION_FACTOR_CLAMP}."
            f"Clamping to {LOWER_BOUND_AERO_POSITION_FACTOR_CLAMP}.",
            UserWarning,
            stacklevel=2,
        )
        return LOWER_BOUND_AERO_POSITION_FACTOR_CLAMP
    if AERO_MULTIPLIER > UPPER_BOUND_AERO_POSITION_FACTOR_CLAMP:
        warnings.warn(
            f"Unusually high AERO_MULTIPLIER={AERO_MULTIPLIER!r}: must be between {LOWER_BOUND_AERO_POSITION_FACTOR_CLAMP} and {UPPER_BOUND_AERO_POSITION_FACTOR_CLAMP}."
            f"Clamping to {UPPER_BOUND_AERO_POSITION_FACTOR_CLAMP}.",
            UserWarning,
            stacklevel=2,
        )
        return UPPER_BOUND_AERO_POSITION_FACTOR_CLAMP

    return AERO_MULTIPLIER   

def _clampSlope(slope_pc: float) -> float:
    if slope_pc < LOWER_BOUND_SLOPE_CLAMP_PC:
        warnings.warn(
            f"Unusually low slope_pc={slope_pc!r}: must be between {LOWER_BOUND_SLOPE_CLAMP_PC} and {UPPER_BOUND_SLOPE_CLAMP_PC}%."
            f"Clamping to {LOWER_BOUND_SLOPE_CLAMP_PC} %.",
            UserWarning,
            stacklevel=2,
        )
        return LOWER_BOUND_SLOPE_CLAMP_PC
    if slope_pc > UPPER_BOUND_SLOPE_CLAMP_PC:
        warnings.warn(
            f"Unusually high slope_pc={slope_pc!r}: must be between {LOWER_BOUND_SLOPE_CLAMP_PC} and {UPPER_BOUND_SLOPE_CLAMP_PC}%."
            f"Clamping to {UPPER_BOUND_SLOPE_CLAMP_PC} %.",
            UserWarning,
            stacklevel=2,
        )
        return UPPER_BOUND_SLOPE_CLAMP_PC
    return slope_pc

def _clampSpeed_kph(velocity_kph: float) -> float:
    if velocity_kph < LOWER_BOUND_SPEED_CLAMP_KPH:
        warnings.warn(
            f"Unusually low velocity_kph={velocity_kph!r}: must be between {LOWER_BOUND_SPEED_CLAMP_KPH} and {UPPER_BOUND_SPEED_CLAMP_KPH} km/h."
            f"Clamping to {LOWER_BOUND_SPEED_CLAMP_KPH} km/h.",
            UserWarning,
            stacklevel=2,
        )
        return LOWER_BOUND_SPEED_CLAMP_KPH
    if velocity_kph > UPPER_BOUND_SPEED_CLAMP_KPH:
        warnings.warn(
            f"Unusually high velocity_kph={velocity_kph!r}: must be between {LOWER_BOUND_SPEED_CLAMP_KPH} and {UPPER_BOUND_SPEED_CLAMP_KPH} km/h."
            f"Clamping to {UPPER_BOUND_SPEED_CLAMP_KPH} km/h.",
            UserWarning,
            stacklevel=2,
        )
        return UPPER_BOUND_SPEED_CLAMP_KPH
    return velocity_kph

def _clampPower(power_watts: float) -> float:
    if power_watts < LOWER_BOUND_POWER_CLAMP_W:
        warnings.warn(
            f"Unusually low power_watts={power_watts!r}: must be between {LOWER_BOUND_POWER_CLAMP_W} and {UPPER_BOUND_POWER_CLAMP_W} W."
            f"Clamping to {LOWER_BOUND_POWER_CLAMP_W} W.",
            UserWarning,
            stacklevel=2,
        )
        return LOWER_BOUND_POWER_CLAMP_W
    if power_watts > UPPER_BOUND_POWER_CLAMP_W:
        warnings.warn(
            f"Unusually high power_watts={power_watts!r}: must be between {LOWER_BOUND_POWER_CLAMP_W} and {UPPER_BOUND_POWER_CLAMP_W} W."
            f"Clamping to {UPPER_BOUND_POWER_CLAMP_W} W.",
            UserWarning,
            stacklevel=2,
        )
        return UPPER_BOUND_POWER_CLAMP_W
    return power_watts

def calculate_rolling_resistance_and_gravity_force(mass_kg: float, slope_pc: float) -> tuple[float, float]:
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

    mass_kg = _clampWeight(mass_kg)
    slope_pc = _clampSlope(slope_pc)

    theta : float = math.atan(slope_pc / 100.0)

    F_roll: float    = COEFFICIENT_Crr * mass_kg * g * math.cos(theta) # always >= 0
    F_gravity: float = mass_kg * g * math.sin(theta)        # <0 descent, >0 climb

    return F_roll, F_gravity

def calculate_frontal_area(height_cm: float, aero_factor: float = AERO_POSITION_FACTOR_TT) -> float:
    """
    Estimate the frontal area (A) of a cyclist in square meters (m^2) using
    a simple formula based on height and riding position multiplier from ChatGPT
    
    Formula:
        A = aero_factor * (0.0155 * height_cm)/100 

    Rationale:
        The actual formula used by Zwift for frontal area is not publicly
        known.

    Args:
        height_cm (float): Rider's height in centimeters.
            Clamped to UPPER_BOUND_HEIGHT_CLAMP_CM or LOWER_BOUND_HEIGHT_CLAMP_CM if invalid.
        aero_factor (float): Multiplier based on rider's position.
            Clamped to UPPER_BOUND_AERO_POSITION_FACTOR_CLAMP or LOWER_BOUND_AERO_POSITION_FACTOR_CLAMP if invalid.
            Defaults to AERO_POSITION_FACTOR_TT, which represents a typical time trial position (not hoods or supertuck).

    Returns:
        float: Frontal area in square meters (m^2).

    Warns:
        UserWarning: If height_cm or aero_factor is outside normal bound, they are 
        clamped to the nearest valid value.
    """

    height_cm = _clampHeight(height_cm)
    aero_factor= _clampAeroMultiplier(aero_factor)

    answer = aero_factor * (0.00155 * height_cm) 

    if answer <= 0.0:
        return LOWER_BOUND_FRONTAL_AREA_CLAMP
    return answer

def calculate_power_from_velocity(velocity_kph: float, height_cm: float, total_mass_kg: float, slope_pc: float, aero_factor: float = AERO_POSITION_FACTOR_TT) -> float:
    """
    Calculate the mechanical power (W) required for a cyclist to maintain
    a specified steady-state velocity, given physical and environmental
    parameters.

    This function implements the full Martin et al. (1998) cycling physics model:

        P = v * (F_aero + F_roll + F_gravity)

    Args:
        velocity_kph (float):
            Steady-state velocity in kilometres per hour (km/h).
        Cd (float):
            Dimensionless aerodynamic drag coefficient. Typical value
            for a road cyclist in the drops: ~0.63.
        height_cm (float):
            Rider height in centimetres (cm).
        Crr (float):
            Dimensionless rolling resistance coefficient. Typical value
            for road tyres on tarmac: ~0.004.
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
    velocity_kph = _clampSpeed_kph(velocity_kph)
    height_cm = _clampHeight(height_cm)
    total_mass_kg = _clampWeight(total_mass_kg)
    slope_pc = _clampSlope(slope_pc)
    aero_factor= _clampAeroMultiplier(aero_factor)

    F_roll, F_gravity = calculate_rolling_resistance_and_gravity_force(total_mass_kg, slope_pc)

    velocity_mps: float = velocity_kph / 3.6  # convert km/h to m/s (1 km/h = 1/3.6 m/s)

    if (velocity_kph > 60.0 and slope_pc >4.0):
        frontal_area = calculate_frontal_area(height_cm, AERO_POSITION_FACTOR_SUPERTUCK)
    else:
        frontal_area = calculate_frontal_area(height_cm, aero_factor)

    F_aero: float = 0.5 * rho * COEFFICIENT_Cd * frontal_area * velocity_mps ** 2

    F_total: float = F_aero + F_roll + F_gravity

    power_w = F_total * velocity_mps

    if (power_w <= 0.0):
        return 0.0

    return power_w

def solve_for_velocity_from_power_using_binary_search(power_watts: float, height_cm: float, total_mass_kg: float, slope_pc: float, aero_factor: float = AERO_POSITION_FACTOR_TT) -> float:
    """
    Solve for the steady-state cycling velocity (km/h) at which a rider
    producing a specified constant power output (W) will travel, given
    the physical and environmental parameters of the rider and road.

    Algorithm
    ---------
    Phase 1 – Upper bound scan:
        Start at 0 kph and step upward in fixed increments until
        calculate_power_from_velocity() first exceeds power_watts.
        That step becomes the upper bound for the binary search.

    Phase 2 – Binary search:
        Bisect [lower_bound_kph, upper_bound_kph] until the interval
        width is within REQUIRED_PRECISION_OF_SPEED_KPH.

    Args:
        power_watts (float):
            Target mechanical power output in watts (W).
        Cd (float):
            Dimensionless aerodynamic drag coefficient. 
        height_cm (float):
            Rider height in centimetres (cm).
        Crr (float):
            Dimensionless rolling resistance coefficient.
        total_mass_kg (float):
            Combined mass of rider and bicycle in kilograms (kg)..
        slope_pc (float):
            Road gradient as a % (rise / run).
            For example, 5 for a 5% climb, -5 for a 5% descent,
            0 for flat terrain.

    Returns:
        float: Steady-state velocity in kilometres per hour (km/h).

    Raises:
        ValueError: If Phase 1 fails to find an upper bound within
            SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND steps.
    """

    power_watts = _clampPower(power_watts)
    height_cm = _clampHeight(height_cm)
    total_mass_kg = _clampWeight(total_mass_kg)
    slope_pc = _clampSlope(slope_pc)

    # 1. Find safe upper bound for binary search.

    CHUNK_OF_KPH_PER_ITERATION = 20.0
    SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND = 20 # must be large enough to reach UPPER_BOUND_SPEED_CLAMP_KPH

    lower_bound_kph: float = 0.0
    upper_bound_kph: float = 0.0

    for _ in range(SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND):
        upper_bound_kph += CHUNK_OF_KPH_PER_ITERATION
        if calculate_power_from_velocity(upper_bound_kph, height_cm=height_cm, total_mass_kg=total_mass_kg, slope_pc=slope_pc, aero_factor=aero_factor) > power_watts:
            break
        lower_bound_kph = upper_bound_kph 
    else:
        raise ValueError(
            f"solve_for_velocity_from_power_using_binary_search failed to find an upper bound "
            f"after {SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND} iterations "
            f"at {power_watts:.1f} W. Maximum speed scanned: {upper_bound_kph:.1f} kph."
        )

    # 2. Binary search within [lower_bound_kph, upper_bound_kph].
    #    Invariant: power(lower_bound_kph) <= power_watts < power(upper_bound_kph)

    REQUIRED_PRECISION_OF_SPEED_KPH = 0.05
    MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION = 30

    binary_search_iterations: int = 0

    while (upper_bound_kph - lower_bound_kph) > REQUIRED_PRECISION_OF_SPEED_KPH and binary_search_iterations < MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION:
        mid_point_kph: float = (lower_bound_kph + upper_bound_kph) / 2.0
        binary_search_iterations += 1
        if calculate_power_from_velocity(mid_point_kph, height_cm=height_cm, total_mass_kg=total_mass_kg, slope_pc=slope_pc, aero_factor=aero_factor) > power_watts:
            upper_bound_kph = mid_point_kph
        else:
            lower_bound_kph = mid_point_kph

    if (upper_bound_kph - lower_bound_kph) > REQUIRED_PRECISION_OF_SPEED_KPH:
        warnings.warn(
            f"solve_for_velocity_from_power_using_binary_search hit the iteration cap "
            f"({MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION} iterations) without "
            f"achieving the required precision of {REQUIRED_PRECISION_OF_SPEED_KPH} kph. "
            f"Residual interval: {upper_bound_kph - lower_bound_kph:.5f} kph "
            f"at {power_watts:.1f} W, slope {slope_pc:.1f}%.",
            UserWarning,
            stacklevel=2,
        )

    # Return lower_bound: the highest speed provably achievable at power_watts.
    return lower_bound_kph

