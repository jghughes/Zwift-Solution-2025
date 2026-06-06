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
   a standard road-cycling position. This value is widely cited as the
   reference target for a typical male road cyclist, and it is the
   default formula in this module. Typical modern road positions 
   with hands on hoods are closer to 0.35 - 0.38. 0.4 m² is quite 
   large (more like an upright climbing position).

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


from calendar import c
import math
import warnings
from scipy.optimize import newton

from constants import COEFFICIENT_g, COEFFICIENT_rho, INITIAL_VELOCITY_GUESS_FOR_NEWTON_SOLVER_KPH, REQUIRED_NEWTON_SOLVER_VELOCITY_PRECISION_KPH, UPPER_BOUND_HEIGHT_CLAMP_CM, LOWER_BOUND_HEIGHT_CLAMP_CM, UPPER_BOUND_WEIGHT_CLAMP_KG, LOWER_BOUND_WEIGHT_CLAMP_KG, LOWER_BOUND_FRONTAL_AREA_CLAMP, LOWER_BOUND_SLOPE_CLAMP_PC, UPPER_BOUND_SLOPE_CLAMP_PC , UPPER_BOUND_SPEED_CLAMP_KPH, LOWER_BOUND_SPEED_CLAMP_KPH, LOWER_BOUND_POWER_CLAMP_W, UPPER_BOUND_POWER_CLAMP_W, ZWIFT_DESCENT_ATTENUATION_FACTOR
from jgh_number import safe_divide

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

def _calculate_rolling_resistance_and_gravity_force(Crr: float, total_mass_kg: float, slope_pc: float) -> tuple[float, float]:
    """
    Calculate the rolling resistance and gravitational forces.

    For negative slopes (descents):
      - sin_theta < 0  →  F_gravity < 0  (gravity assists motion)
      - cos_theta > 0  →  F_roll   > 0  (rolling resistance always opposes motion)

    Note the attenuation factor applied to descents to reflect Zwift's physics 
    model, which limits maximum speeds on descents. 

    Returns:
        tuple[float, float]: (F_roll, F_gravity)
            F_roll   is always >= 0
            F_gravity is negative on descents, positive on climbs
    """

    total_mass_kg = _clampWeight(total_mass_kg)
    slope_pc = _clampSlope(slope_pc)

    if slope_pc < 0.0:
        slope_pc *= ZWIFT_DESCENT_ATTENUATION_FACTOR

    theta : float = math.atan(slope_pc / 100.0)

    F_roll: float    = Crr * total_mass_kg * g * math.cos(theta) # always >= 0
    F_gravity: float = total_mass_kg * g * math.sin(theta)        # <0 descent, >0 climb

    return F_roll, F_gravity

def calculate_frontal_area(height_cm: float, weight_kg: float) -> float:
    """
    Estimate the frontal area (A) of a cyclist in square meters (m^2) using
    a simple linear formula based on both height and weight.

    Formula:
        A = 0.0022 * height_cm + 0.0016 * weight_kg - 0.1226

    Rationale:
        The actual formula used by Zwift for frontal area is not publicly
        known and may not include height or weight at all. Much cycling 
        physics literature and simulation platforms use a fixed value around
        0.4 m^2 for a typical road cyclist. This linear formula is calibrated
        so that for a man 183 cm tall and 75 kg, the answer is approximately
        0.4 m^2, matching the value commonly cited in the literature.

    Args:
        height_cm (float): Rider's height in centimeters.
            Clamped to UPPER_BOUND_HEIGHT_CLAMP_CM or LOWER_BOUND_HEIGHT_CLAMP_CM if invalid.
        weight_kg (float): Rider's weight in kilograms.
            Clamped to UPPER_BOUND_WEIGHT_CLAMP_KG or LOWER_BOUND_WEIGHT_CLAMP_KG if invalid.

    Returns:
        float: Frontal area in square meters (m^2).

    Warns:
        UserWarning: If height_cm or weight_kg is outside normal bound, they are 
        clamped to the nearest valid value.
    """

    height_cm = _clampHeight(height_cm)
    weight_kg = _clampWeight(weight_kg)

    # To yield exactly 0.4 m² for (183 cm, 75 kg): (Zwift Insider's dimensions)
    # 0.0022*183 + 0.0016*75 - C = 0.4
    # C = 0.5226 - 0.4 = 0.1226
    answer = 0.0022 * height_cm + 0.0016 * weight_kg - 0.1226

    if answer <= 0.0:
        warnings.warn(
            f"Computed frontal area {answer:.4f} m² is non-positive for "
            f"height_cm={height_cm}, weight_kg={weight_kg}. "
            f"Defaulting to {LOWER_BOUND_FRONTAL_AREA_CLAMP} m².",
            UserWarning,
            stacklevel=2,
        )
        return LOWER_BOUND_FRONTAL_AREA_CLAMP
    return answer

def calculate_power_from_velocity(velocity_kph: float, Cd: float, height_cm: float, Crr: float, total_mass_kg: float, slope_pc: float) -> float:
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

    F_roll, F_gravity = _calculate_rolling_resistance_and_gravity_force(Crr, total_mass_kg, slope_pc)

    velocity_mps: float = velocity_kph / 3.6  # convert km/h to m/s (1 km/h = 1/3.6 m/s)

    frontal_area = calculate_frontal_area(height_cm, total_mass_kg)

    F_aero: float = 0.5 * rho * Cd * frontal_area * velocity_mps ** 2

    F_total: float = F_aero + F_roll + F_gravity

    return F_total * velocity_mps

def solve_for_velocity_from_power_using_binary_search(power_watts: float, Cd: float, height_cm: float, Crr: float, total_mass_kg: float, slope_pc: float) -> float:
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
        if calculate_power_from_velocity(upper_bound_kph, Cd, height_cm=height_cm, Crr=Crr, total_mass_kg=total_mass_kg, slope_pc=slope_pc) > power_watts:
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
        if calculate_power_from_velocity(mid_point_kph, Cd, height_cm=height_cm, Crr=Crr, total_mass_kg=total_mass_kg, slope_pc=slope_pc) > power_watts:
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

# def solve_for_velocity_from_power_using_newton(power_watts: float, Cd: float, height_cm: float, Crr: float, total_mass_kg: float, slope_pc: float) -> float:
#     """
#     Solve for the steady-state cycling velocity (km/h) at which a rider
#     producing a specified constant power output (W) will travel, given
#     the physical and environmental parameters of the rider and road.

#     Problem formulation
#     -------------------
#     The Martin et al. (1998) power model gives power as a function of
#     velocity:

#         P(v) = v * (F_aero(v) + F_roll + F_gravity)

#     where v is velocity in m/s. This function inverts that relationship:
#     given P, find v such that P(v) - power_watts = 0. Because P(v) is a
#     strictly increasing cubic in v for positive resistance forces, there
#     is exactly one positive real root, which is the physically meaningful
#     steady-state velocity.

#     Numerical method
#     ----------------
#     The root is found using the Newton-Raphson method (scipy.optimize.
#     newton), supplied with both the residual function P(v) - power_watts
#     and its analytic derivative dP/dv. This gives fast quadratic
#     convergence, typically in 4-6 iterations from the initial estimate.
#     The analytic derivative is:

#         dP/dv = F_total(v) + v * dF_aero/dv
#               = (F_aero + F_roll + F_gravity) + v * (rho * Cd * area * v)

#     Only F_aero depends on v; F_roll and F_gravity are constant for a
#     given slope and total mass.

#     Args:
#         power_watts (float):
#             Target mechanical power output in watts (W). Must be
#             strictly positive; raises ValueError otherwise.
#         Cd (float):
#             Dimensionless aerodynamic drag coefficient. Typical value
#             for a road cyclist in the drops: ~0.63.
#         height_cm (float):
#             Rider height in centimetres (cm). Typical value for a
#             road cyclist: ~183 cm. See calculate_frontal_area() for estimation.
#         Crr (float):
#             Dimensionless rolling resistance coefficient. Typical value
#             for road tyres on tarmac: ~0.004.
#         total_mass_kg (float):
#             Combined mass of rider and bicycle in kilograms (kg).
#         slope_pc (float):
#             Road gradient as a % (rise / run).
#             For example, 5 for a 5% for a climb, -5 for a 5% descent,
#             0 for flat terrain.

#     Returns:
#         float: Steady-state velocity in kilometres per hour (km/h).

#     Raises:
#         ValueError: If power_watts <= 0.
#         ValueError: If the Newton-Raphson solver fails to converge
#             (wraps the underlying scipy RuntimeError).
#         ValueError: If the solver converges to a non-physical
#             (zero or negative) velocity.

#     Internal variables:
#         equation (callable):       Residual P(v) - power_watts (W).
#         equation_prime (callable): Analytic derivative dP/dv (W·s/m).
#         v (float):                 Speed in m/s, local to the closures.
#         F_aero (float):            Aerodynamic drag force, N.
#         F_roll (float):            Rolling resistance force, N.
#         F_gravity (float):         Gravitational force along slope, N.
#         F_total (float):           Sum of all resistive forces, N.
#         dF_aero_dv (float):        d(F_aero)/dv = rho*Cd*area*v, N·s/m.
#         dF_total_dv (float):       d(F_total)/dv = dF_aero_dv, N·s/m.
#         _hyp (float):              sqrt(1 + slope^2), dimensionless.
#         v_solution (float):        Newton-Raphson root in m/s.
#     """

#     power_watts = _clampPower(power_watts)
#     height_cm = _clampHeight(height_cm)
#     total_mass_kg = _clampWeight(total_mass_kg)
#     slope_pc = _clampSlope(slope_pc)

#     _F_roll, _F_gravity = _calculate_rolling_resistance_and_gravity_force(Crr, total_mass_kg, slope_pc)

#     def delta_power_equation(velocity_mps: float) -> float:
#         F_aero: float = 0.5 * rho * Cd * frontal_area * velocity_mps ** 2
#         return velocity_mps * (F_aero + _F_roll + _F_gravity) - power_watts

#     def power_derivative_equation(velocity_mps: float) -> float:
#         F_aero: float = 0.5 * rho * Cd * frontal_area * velocity_mps ** 2
#         F_total: float = F_aero + _F_roll + _F_gravity
#         dF_aero_dv: float = rho * Cd * frontal_area * velocity_mps  # Only F_aero depends on velocity_mps
#         return F_total + velocity_mps * dF_aero_dv

#     def estimate_initial_velocity_mps(power_watts: float, Cd: float, height_cm: float, total_mass_kg: float, slope_pc: float,
#     ) -> float:
#         """
#         Estimate a starting guess (m/s) for the Newton-Raphson solver.

#         On gentle or flat terrain the fixed constant
#         INITIAL_VELOCITY_GUESS_FOR_NEWTON_SOLVER_KPH is adequate.  On steep
#         descents a rider producing significant power can exceed 120 km/h, so
#         the fixed guess may fall below the actual solution and land in the
#         region where dP/dv < 0, causing the solver to diverge.

#         The estimate is derived in two steps:

#             1.  Coasting terminal velocity (gravity balances aero drag, P = 0):
#                     v_terminal = sqrt(F_gravity / (0.5 * rho * CdA))

#             2.  Power-aware estimate.  At the actual solution v*, aero drag
#                 must absorb BOTH the rider's mechanical power AND the
#                 gravitational energy rate F_gravity * v*.  Substituting
#                 v_terminal for v* on the right-hand side (an underestimate,
#                 so the result remains below v*) and solving for v:
#                     v_estimate = ((power_watts + F_gravity * v_terminal)
#                                   / (0.5 * rho * CdA)) ** (1/3)

#             A 10 % safety margin is added so the guess sits above v* in the
#             region where dP/dv > 0 and Newton-Raphson converges reliably.

#         Args:
#             power_watts (float):  Rider's mechanical power output (W).
#             Cd (float):           Aerodynamic drag coefficient (dimensionless).
#             frontal_area (float): Frontal area (m^2).
#             total_mass (float):   Rider + bike mass (kg).
#             slope_pc (float):     Road gradient (%).  Negative = descent.

#         Returns:
#             float: Initial velocity guess in m/s.
#         """

#         height_cm = _clampHeight(height_cm)
#         total_mass_kg = _clampWeight(total_mass_kg)

#         base_kph = INITIAL_VELOCITY_GUESS_FOR_NEWTON_SOLVER_KPH

#         if slope_pc < -5.0:
#             cda: float = Cd * calculate_frontal_area(height_cm, total_mass_kg)
#             f_gravity: float = total_mass_kg * g * abs(slope_pc) / 100.0

#             # Step 1: coasting terminal velocity
#             v_terminal: float = math.sqrt(f_gravity / (0.5 * rho * cda))

#             # Step 2: estimate accounting for actual power output
#             v_estimate: float = ((power_watts + f_gravity * v_terminal) / (0.5 * rho * cda)) ** (1.0 / 3.0)

#             # 10% buffer above estimate, never below the flat-terrain default
#             base_kph = max(base_kph, v_estimate * 3.6 * 1.1)

#         return base_kph / 3.6

#     initial_estimate_of_root_meters_per_sec: float = estimate_initial_velocity_mps(power_watts, Cd, height_cm, total_mass_kg, slope_pc)

#     required_precision_meters_per_sec: float = REQUIRED_NEWTON_SOLVER_VELOCITY_PRECISION_KPH / 3.6

#     try:
#         v_solution: float = newton(func=delta_power_equation, x0=initial_estimate_of_root_meters_per_sec, fprime=power_derivative_equation, tol=required_precision_meters_per_sec)
#     except RuntimeError as e:
#         raise ValueError(f"solve_for_velocity_from_power_using_newton failed to converge: {e}") from e

#     if v_solution < 0.0:
#         raise ValueError(f"Solver returned negative velocity: {v_solution:.4f} m/s")

#     return v_solution * 3.6
