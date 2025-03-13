import logging
from jgh_logging import jgh_configure_logging
import numpy as np
from models import * 

# Configure logging
jgh_configure_logging("appsettings.json")
logger= logging.getLogger(__name__)

# units of power (w) = watts
# units of velocity (v) = m/s
# coefficient of drag of cyclist (c) = 0.5
# frontal area of cyclist (a) = 0.5 m^2

# w = c * a * (v^3)
# height of cyclist (cm) = 183
# weight of cyclist (kg) = 75
# gender of cyclist (enum) m



# Define the ZwiftInsiderWattageMatrix
ZwiftInsiderWattageMatrix = np.array([
    [300, 350, 400],
    [212, 252, 290],
    [196, 236, 261],
    [191, 217, 255]
])

# Define the ZwiftInsiderVelocityMatrix_kph (km/h)
ZwiftInsiderVelocityMatrix_kph = np.array([39.9, 42.2, 44.4])

# Convert the velocity matrix to m/s
ZwiftInsiderVelocityMatrix_ms = ZwiftInsiderVelocityMatrix_kph * 1000 / 3600

# Define the ZwiftInsiderDraftPowerMatrix
ZwiftInsiderDraftPowerMatrix = ZwiftInsiderWattageMatrix / ZwiftInsiderWattageMatrix[0, :]


# Example usage

def main():
    logger.info("ZwiftInsiderWattageMatrix:")
    logger.info(ZwiftInsiderWattageMatrix)
    logger.info("ZwiftInsiderVelocityMatrix_kph:")
    logger.info(ZwiftInsiderVelocityMatrix_kph)

    # # Create the velocity matrix with the same shape as ZwiftInsiderWattageMatrix
    velocity_matrix = np.tile(ZwiftInsiderVelocityMatrix_kph, (ZwiftInsiderWattageMatrix.shape[0], 1))
    logger.info("Velocity Matrix (km/h):")
    logger.info(velocity_matrix)

    logger.info("ZwiftInsiderDraftPowerMatrix:")
    logger.info(ZwiftInsiderDraftPowerMatrix)

    # Instantiate the default Rider named ericschlange
    ericschlange = Rider(
        zwiftid=12345,
        name="Eric Schlange",
        weight=84.3,
        height=180,
        gender=Gender.MALE,
        ftp=272,
        zwift_racing_score=549,
        velo_rating=1513
    )

    # Create a 1xn matrix for power values ranging from 300 to 500 watts in 50-watt increments
    power_values = np.arange(300, 501, 50)
    velocity_matrix_kph = np.array([ericschlange.calculate_speed_from_power(power) for power in power_values])
    logger.info("Velocity Matrix (km/h):")
    logger.info(velocity_matrix_kph)


if __name__ == "__main__":
    main()

