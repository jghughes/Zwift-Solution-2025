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
import warnings


from constants import (
    COEFFICIENT_g, 
    COEFFICIENT_rho,
    COEFFICIENT_Cd,
    COEFFICIENT_Crr, 
    COEFFICIENT_bike_weight_kg,
    AERO_POSITION_FACTOR_DEFAULT,
    DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC,
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
    answer: float = aero_factor * (0.00155 * height_cm) 
    return answer


def calculate_CdA(height_cm: float, aero_factor: float) -> float:
    """
    Estimate CdA from rider height (cm) and aero factor (unitless); returns CdA (m^2).
    """
    effective_frontal_area: float = calculate_frontal_area(height_cm, aero_factor)
    return COEFFICIENT_Cd * effective_frontal_area


def calculate_power_from_velocity(velocity_kph: float, height_cm: float, total_mass_kg: float, slope_pc: float = DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC, aero_factor: float = AERO_POSITION_FACTOR_DEFAULT) -> float:
    """
    Return required watts from speed (km/h), rider weight (kg), 
    rider height (cm), and slope (%); returns watts (W).
    """
    F_roll, F_gravity = calculate_rolling_resistance_and_gravity_force(total_mass_kg, slope_pc)

    velocity_mps: float = velocity_kph / 3.6  

    CdA: float = calculate_CdA(height_cm, aero_factor)
    F_aero: float = 0.5 * COEFFICIENT_rho * CdA * velocity_mps ** 2

    F_total: float = F_aero + F_roll + F_gravity

    power_w: float = F_total * velocity_mps

    if (power_w <= 0.0):
        return 0.0

    return power_w


def calculate_velocity_from_power(power_watts: float, height_cm: float, total_mass_kg: float, slope_pc: float = DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC, aero_factor: float = AERO_POSITION_FACTOR_DEFAULT) -> float:
    return solve_for_velocity_from_power_using_binary_search(power_watts, height_cm, total_mass_kg, slope_pc, aero_factor)
    # return solve_for_velocity_from_power_using_formula_for_cubics(power_watts, height_cm, total_mass_kg, slope_pc, aero_factor)
    

def solve_for_velocity_from_power_using_formula_for_cubics(power_watts: float, height_cm: float, total_mass_kg: float, slope_pc: float = DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC, aero_factor: float = AERO_POSITION_FACTOR_DEFAULT) -> float:
    """
    Return equilibrium speed (km/h) for a given power output (W), rider
    height (cm), total mass (kg), and slope (%).

    Physics (Martin et al., 1998)
    ==============================
    The power-speed relation (see calculate_power_from_velocity) expands to:

        P = A_coef * v^3 + B_coef * v

    where
        A_coef = 0.5 * rho * CdA          (kg/m, always > 0)
        B_coef = Crr*m*g*cos(theta)
                 + m*g*sin(theta)          (N; > 0 uphill, < 0 on descent)
        theta  = atan(slope_pc / 100)      (radians)

    Dividing through by A_coef gives the depressed cubic (no t^2 term):

        t^3 + p*t + q = 0

    where t = v (m/s) and
        p = B_coef / A_coef
        q = -P / A_coef

    References
    ----------
    Wikipedia, "Cubic equation",
    https://en.wikipedia.org/wiki/Cubic_equation

    Nickalls, R.W.D. (2006). "Viete, Descartes, and the cubic equation."
    Mathematical Gazette, 90(518), 203-208.
    DOI: 10.1017/S0025557200179598

    Discriminant (Wikipedia section 4.1)
    =====================================

        Discriminant = -(4*p^3 + 27*q^2)

        Discriminant <= 0  =>  one real root    =>  Cardano's formula
        Discriminant >  0  =>  three real roots =>  Viete's formula

    For cycling ranges of -16% to +16% slope and P >= 0 W, the Viete
    branch applies for descents of roughly -4% or steeper across the
    full practical power range (0 to ~1500 W).

    Cardano's formula (Wikipedia section 5)
    =========================================
    Valid when Discriminant <= 0. One real root, two complex conjugates.

        D  = q^2/4 + p^3/27
        u1 = -q/2 + sqrt(D)
        C  = cbrt(u1)          (real cube root, sign-preserving)
        t  = C - p/(3*C)

    Viete's trigonometric formula (Wikipedia section 7.1)
    =======================================================
    Valid when Discriminant > 0. Three distinct real roots (casus irreducibilis).
    p < 0 is guaranteed in this branch.

        m   = 2 * sqrt(-p/3)
        phi = arccos( (3*q)/(2*p) * sqrt(-3/p) )
        t_k = m * cos(phi/3 - 2*pi*k/3)    for k = 0, 1, 2

    Only k=0 is computed. It gives the largest root and is the physically
    correct equilibrium speed in all descent conditions.
    """
    # --- physics: resolve forces and aerodynamic drag area -------------------
    F_roll, F_gravity = calculate_rolling_resistance_and_gravity_force(total_mass_kg, slope_pc)
    CdA: float = calculate_CdA(height_cm, aero_factor)

    A_coef: float = 0.5 * COEFFICIENT_rho * CdA   # must always be > 0  (kg/m) (0.0 will blow up, divide by zero below)
    B_coef: float = F_roll + F_gravity             # N; sign depends on slope

    # --- depressed cubic: t^3 + p*t + q = 0 (Wikipedia section 3) ----------
    p: float = B_coef / A_coef
    q: float = -power_watts / A_coef

    # --- discriminant (Discriminant) (Wikipedia section 4.1) --------------------------------
    Discriminant: float = -(4.0 * p**3 + 27.0 * q**2)

    t: float = 0.0

    if Discriminant <= 0.0:
        # --- Cardano's formula (Wikipedia section 5) -------------------------
        D: float  = q**2 / 4.0 + p**3 / 27.0
        u1: float = -q / 2.0 + math.sqrt(D)
        C: float  = math.copysign(abs(u1) ** (1.0 / 3.0), u1)
        t = 0.0 if C == 0.0 else C - p / (3.0 * C)

    else:
        # --- Viete's trigonometric formula (Wikipedia section 7.1) ----------
        m: float   = 2.0 * math.sqrt(-p / 3.0)
        phi: float = math.acos((3.0 * q) / (2.0 * p) * math.sqrt(-3.0 / p))
        t = m * math.cos(phi / 3.0)          # k=0: largest real root

    velocity_mps: float = max(0.0, t)
    return velocity_mps * 3.6               # m/s -> km/h


def solve_for_velocity_from_power_using_binary_search(power_watts: float, height_cm: float, total_mass_kg: float, slope_pc: float = DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC, aero_factor: float = AERO_POSITION_FACTOR_DEFAULT) -> float:
    """
    Solve for the steady-state cycling velocity (km/h) at which a rider
    producing a specified constant power output (W) will travel, given
    the physical and environmental parameters of the rider and road.
    Defaults to a typical time-trial position for the 
    aero factor, which is not the same as the hoods position 
    or the supertuck position.


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
        aero_factor (float):
            Dimensionless aerodynamic factor. 
            Defaults to a typical time-trial position.
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

    if (power_watts <= 0.0):
        return 0.0

    # 1. Find safe upper bound for binary search

    CHUNK_OF_KPH_PER_ITERATION = 20.0
    SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND = 30 

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

    # 2. Binary search

    REQUIRED_PRECISION_OF_SPEED_KPH = 0.001
    MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION = 100

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






