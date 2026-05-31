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


import math
import warnings
from scipy.optimize import newton

from constants import COEFFICIENT_g, COEFFICIENT_rho, INITIAL_VELOCITY_GUESS_FOR_NEWTON_SOLVER_KPH, REQUIRED_NEWTON_SOLVER_VELOCITY_PRECISION_KPH, UPPER_BOUND_HEIGHT_CLAMP_CM, LOWER_BOUND_HEIGHT_CLAMP_CM, UPPER_BOUND_WEIGHT_CLAMP_KG, LOWER_BOUND_WEIGHT_CLAMP_KG, LOWER_BOUND_FRONTAL_AREA_CLAMP

# abbreviations
g: float = COEFFICIENT_g  # gravity (m/s^2)
rho: float = COEFFICIENT_rho  # air density at sea level (kg/m^3)

def _validate_physical_params(Cd: float, area : float, Crr: float, total_mass: float,) -> None:
    """
    Validate that the physical parameters passed to the cycling power
    model are within plausible positive bounds.

    All four parameters must be strictly positive; zero or negative
    values are physically meaningless and will produce incorrect power
    or velocity results without raising an obvious error.

    Args:
        Cd (float):         Drag coefficient (dimensionless).
        A (float):          Frontal area (m^2).
        Crr (float):        Rolling resistance coefficient (dimensionless).
        total_mass (float): Combined rider + bike mass (kg).

    Raises:
        ValueError: If any parameter is zero or negative, with a
            message identifying the offending parameter and its value.
    """
    if Cd < 0.0:
        raise ValueError(f"Cd must be non-negative, got {Cd}")
    if area < 0.0:
        raise ValueError(f"area must be non-negative, got {area}")
    if Crr < 0.0:
        raise ValueError(f"Crr must be non-negative, got {Crr}")
    if total_mass < 0.0:
        raise ValueError(f"total_mass must be non-negative, got {total_mass}")


def _calculate_gravity_and_rolling_forces(Crr: float, total_mass: float, slope: float) -> tuple[float, float]:
    """
    Calculate the rolling resistance and gravitational forces.
    Treats 'slope' as sin(theta) (rise over hypotenuse, standard for cycling grades).
    
    Returns:
        tuple[float, float]: (F_roll, F_gravity)
    """
    if slope == 0.0:
        return Crr * total_mass * g, 0.0

    # cos(theta) = sqrt(1 - sin^2(theta))
    # max() prevents a math domain error if a logically invalid slope > 1.0 or < -1.0 is passed.
    cos_theta: float = math.sqrt(max(0.0, 1.0 - slope * slope))
    
    F_roll: float = Crr * total_mass * g * cos_theta
    F_gravity: float = total_mass * g * slope
    
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
    if height_cm < LOWER_BOUND_HEIGHT_CLAMP_CM:
        warnings.warn(
            f"Unusually short height_cm={height_cm!r}: must be between {LOWER_BOUND_HEIGHT_CLAMP_CM} and {UPPER_BOUND_HEIGHT_CLAMP_CM} cm."
            f"Clamping to {LOWER_BOUND_HEIGHT_CLAMP_CM} cm.",
            UserWarning,
            stacklevel=2,
        )
        height_cm = LOWER_BOUND_HEIGHT_CLAMP_CM

    if height_cm > UPPER_BOUND_HEIGHT_CLAMP_CM:
        warnings.warn(
            f"Unusually tall height_cm={height_cm!r}: must be between {LOWER_BOUND_HEIGHT_CLAMP_CM} and {UPPER_BOUND_HEIGHT_CLAMP_CM} cm. "
            f"Clamping to {UPPER_BOUND_HEIGHT_CLAMP_CM} cm.",
            UserWarning,
            stacklevel=2,
        )
        height_cm = UPPER_BOUND_HEIGHT_CLAMP_CM

    if weight_kg < LOWER_BOUND_WEIGHT_CLAMP_KG:
        warnings.warn(
            f"Unusually low weight_kg={weight_kg!r}: must be between {LOWER_BOUND_WEIGHT_CLAMP_KG} and {UPPER_BOUND_WEIGHT_CLAMP_KG} kg. "
            f"Clamping to {LOWER_BOUND_WEIGHT_CLAMP_KG} kg.",
            UserWarning,
            stacklevel=2,
        )
        weight_kg = LOWER_BOUND_WEIGHT_CLAMP_KG

    if weight_kg > UPPER_BOUND_WEIGHT_CLAMP_KG:
        warnings.warn(
            f"Unusually heavy weight_kg={weight_kg!r}: must be between {LOWER_BOUND_WEIGHT_CLAMP_KG} and {UPPER_BOUND_WEIGHT_CLAMP_KG} kg. "
            f"Clamping to {UPPER_BOUND_WEIGHT_CLAMP_KG} kg.",
            UserWarning,
            stacklevel=2,
        )
        weight_kg = UPPER_BOUND_WEIGHT_CLAMP_KG

    # To yield exactly 0.4 m² for (183 cm, 75 kg): (Zwift Insider's dimensions)
    # 0.0022*183 + 0.0016*75 - C = 0.4
    # C = 0.5226 - 0.4 = 0.1226
    # answer = 0.0016 * weight_kg - 0.1226 # test rubbish formula that only depends on weight
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


def calculate_power_required(velocity_m_per_s: float, Cd: float, A: float, Crr: float, total_mass: float, slope: float) -> float:
    """
    Calculate the mechanical power (W) required for a cyclist to maintain
    a constant velocity, accounting for aerodynamic drag, rolling resistance,
    and gravitational force on a gradient.

    The model is based on Martin et al. (1998) and implements:

        P = v * (F_aero + F_roll + F_gravity)

    where each force component is:

        F_aero    = 0.5 * rho * Cd * A * v^2          [N]
        F_roll    = Crr * total_mass * g * cos(theta)  [N]
        F_gravity = total_mass * g * sin(theta)        [N]

    and theta = atan(slope) is the road angle in radians.

    The trig terms are evaluated using the closed-form identities:

        sin(atan(slope)) = slope / sqrt(1 + slope^2)
        cos(atan(slope)) = 1     / sqrt(1 + slope^2)

    to avoid the overhead of calling atan() during Newton-Raphson
    iteration. When slope == 0.0 all trig is bypassed entirely:
    cos(theta) = 1 and sin(theta) = 0 exactly.

    A negative slope (descent) causes F_gravity to become negative,
    correctly reducing the required power. No special-casing is needed.

    Args:
        velocity_m_per_s (float):
            Cyclist velocity in metres per second (m/s). Must be >= 0.
        Cd (float):
            Dimensionless aerodynamic drag coefficient. Typical value
            for a road cyclist in the drops: ~0.63.
        area (float):
            Frontal area in square metres (m^2). Typical value for a
            road cyclist: ~0.4 m^2. See calculate_frontal_area() for estimation.
        Crr (float):
            Dimensionless rolling resistance coefficient. Typical value
            for road tyres on tarmac: ~0.004.
        total_mass (float):
            Combined mass of rider and bicycle in kilograms (kg).
        slope (float):
            Road gradient expressed as a dimensionless ratio
            (rise / run). For example, a 5% climb is slope = 0.05,
            a 5% descent is slope = -0.05. Flat terrain is slope = 0.0.

    Returns:
        float: Required mechanical power in watts (W).

    Internal variables:
        rho (float):  Air density at sea level, kg/m^3 (from constants).
        g   (float):  Gravitational acceleration, m/s^2 (from constants).
        F_aero (float):    Aerodynamic drag force, N.
        F_roll (float):    Rolling resistance force, N.
        F_gravity (float): Gravitational component force along slope, N.
        F_total (float):   Sum of all resistive forces, N.
        _hyp (float):      sqrt(1 + slope^2), dimensionless; used to
                           evaluate sin and cos of atan(slope) without
                           calling atan().
    """

    F_aero: float = 0.5 * rho * Cd * A * velocity_m_per_s ** 2

    F_roll, F_gravity = _calculate_gravity_and_rolling_forces(Crr, total_mass, slope)

    F_total: float = F_aero + F_roll + F_gravity

    return velocity_m_per_s * F_total

def solve_velocity_from_power(power_watts: float, Cd: float, area: float, Crr: float, total_mass: float, slope: float) -> float:
    """
    Solve for the steady-state cycling velocity (km/h) at which a rider
    producing a specified constant power output (W) will travel, given
    the physical and environmental parameters of the rider and road.

    Problem formulation
    -------------------
    The Martin et al. (1998) power model gives power as a function of
    velocity:

        P(v) = v * (F_aero(v) + F_roll + F_gravity)

    where v is velocity in m/s. This function inverts that relationship:
    given P, find v such that P(v) - power_watts = 0. Because P(v) is a
    strictly increasing cubic in v for positive resistance forces, there
    is exactly one positive real root, which is the physically meaningful
    steady-state velocity.

    Numerical method
    ----------------
    The root is found using the Newton-Raphson method (scipy.optimize.
    newton), supplied with both the residual function P(v) - power_watts
    and its analytic derivative dP/dv. This gives fast quadratic
    convergence, typically in 4-6 iterations from the initial estimate.
    The analytic derivative is:

        dP/dv = F_total(v) + v * dF_aero/dv
              = (F_aero + F_roll + F_gravity) + v * (rho * Cd * area * v)

    Only F_aero depends on v; F_roll and F_gravity are constant for a
    given slope and total mass.

    Args:
        power_watts (float):
            Target mechanical power output in watts (W). Must be
            strictly positive; raises ValueError otherwise.
        Cd (float):
            Dimensionless aerodynamic drag coefficient. Typical value
            for a road cyclist in the drops: ~0.63.
        area (float):
            Frontal area in square metres (m^2). Typical value for a
            road cyclist: ~0.4 m^2. See calculate_frontal_area() for estimation.
        Crr (float):
            Dimensionless rolling resistance coefficient. Typical value
            for road tyres on tarmac: ~0.004.
        total_mass (float):
            Combined mass of rider and bicycle in kilograms (kg).
        slope (float):
            Road gradient as a dimensionless ratio (rise / run).
            For example, 0.05 for a 5% climb, -0.05 for a 5% descent,
            0.0 for flat terrain.

    Returns:
        float: Steady-state velocity in kilometres per hour (km/h).

    Raises:
        ValueError: If power_watts <= 0.
        ValueError: If the Newton-Raphson solver fails to converge
            (wraps the underlying scipy RuntimeError).
        ValueError: If the solver converges to a non-physical
            (zero or negative) velocity.

    Internal variables:
        equation (callable):       Residual P(v) - power_watts (W).
        equation_prime (callable): Analytic derivative dP/dv (W·s/m).
        v (float):                 Speed in m/s, local to the closures.
        F_aero (float):            Aerodynamic drag force, N.
        F_roll (float):            Rolling resistance force, N.
        F_gravity (float):         Gravitational force along slope, N.
        F_total (float):           Sum of all resistive forces, N.
        dF_aero_dv (float):        d(F_aero)/dv = rho*Cd*area*v, N·s/m.
        dF_total_dv (float):       d(F_total)/dv = dF_aero_dv, N·s/m.
        _hyp (float):              sqrt(1 + slope^2), dimensionless.
        v_solution (float):        Newton-Raphson root in m/s.
    """

    _validate_physical_params(Cd, area, Crr, total_mass)

    if power_watts <= 0.0:
        raise ValueError(f"power_watts must be positive, got {power_watts}")

    # F_roll and F_gravity are independent of velocity; precompute once
    # so both closures share the same values and cannot drift.
    _F_roll, _F_gravity = _calculate_gravity_and_rolling_forces(Crr, total_mass, slope)

    def power_difference_equation(velocity_mps: float) -> float:
        F_aero: float = 0.5 * rho * Cd * area * velocity_mps ** 2
        return velocity_mps * (F_aero + _F_roll + _F_gravity) - power_watts

    def power_derivative_equation(velocity_mps: float) -> float:
        F_aero: float = 0.5 * rho * Cd * area * velocity_mps ** 2
        F_total: float = F_aero + _F_roll + _F_gravity
        dF_aero_dv: float = rho * Cd * area * velocity_mps  # Only F_aero depends on velocity_mps
        return F_total + velocity_mps * dF_aero_dv

    initial_estimate_of_root_meters_per_sec: float = INITIAL_VELOCITY_GUESS_FOR_NEWTON_SOLVER_KPH / 3.6
    required_precision_meters_per_sec: float = REQUIRED_NEWTON_SOLVER_VELOCITY_PRECISION_KPH / 3.6
    try:
        v_solution: float = newton(power_difference_equation, initial_estimate_of_root_meters_per_sec, fprime=power_derivative_equation, tol=required_precision_meters_per_sec)
    except RuntimeError as e:
        raise ValueError(f"solve_velocity_from_power failed to converge: {e}") from e

    if v_solution < 0.0:
        raise ValueError(f"Solver returned negative velocity: {v_solution:.4f} m/s")

    return v_solution * 3.6  # convert to kph

def solve_power_from_velocity(velocity_kph: float, Cd: float, area: float, Crr: float, total_mass: float, slope: float) -> float:
    """
    Calculate the mechanical power (W) required for a cyclist to maintain
    a specified steady-state velocity, given physical and environmental
    parameters.

    This function is a thin unit-conversion wrapper around
    calculate_power_required(). It converts the input velocity from km/h to m/s
    (dividing by 3.6, since 1 km/h = 1000/3600 m/s) and delegates
    directly to calculate_power_required(), which implements the full Martin et al.
    (1998) cycling physics model:

        P = v * (F_aero + F_roll + F_gravity)

    See calculate_power_required() for full details of the physics, the force
    components, and the trig optimisations used for non-zero slopes.

    Args:
        velocity_kph (float):
            Target steady-state velocity in kilometres per hour (km/h).
            Should be positive; passing zero or a negative value will
            produce zero or negative power, which is physically
            meaningless but is not explicitly guarded here — validation
            is the caller's responsibility.
        Cd (float):
            Dimensionless aerodynamic drag coefficient. Typical value
            for a road cyclist in the drops: ~0.63.
        area (float):
            Frontal area in square metres (m^2). Typical value for a
            road cyclist: ~0.4 m^2. See calculate_frontal_area() for estimation.
        Crr (float):
            Dimensionless rolling resistance coefficient. Typical value
            for road tyres on tarmac: ~0.004.
        total_mass (float):
            Combined mass of rider and bicycle in kilograms (kg).
        slope (float):
            Road gradient as a dimensionless ratio (rise / run).
            For example, 0.05 for a 5% climb, -0.05 for a 5% descent,
            0.0 for flat terrain.

    Returns:
        float: Required mechanical power in watts (W).

    Internal variables:
        velocity_mps (float): Speed converted to metres per second (m/s),
                   computed as velocity_kph / 3.6.
    """

    _validate_physical_params(Cd, area, Crr, total_mass)
    if velocity_kph < 0.0:
        raise ValueError(f"velocity_kph must be non-negative, got {velocity_kph}")

    velocity_mps: float = velocity_kph / 3.6  # convert km/h to m/s (1 km/h = 1/3.6 m/s)
    return calculate_power_required(velocity_mps, Cd, area, Crr, total_mass, slope)