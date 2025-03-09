import logging
from jgh_logging import jgh_configure_logging
import numpy as np
import formulae as formula

# Configure logging
jgh_configure_logging("appsettings.json")
logger= logging.getLogger(__name__)

# units of power (w) = watts
# units of velocity (v) = m/s
# coefficient of drag of cyclist (c) = 0.5
# frontal area of cyclist (a) = 0.5 m^2

# w = c * a * (v^3)



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


# Example usage

def main():
    logger.info("ZwiftInsiderWattageMatrix:")
    logger.info(ZwiftInsiderWattageMatrix)
    logger.info("ZwiftInsiderVelocityMatrix_kph:")
    logger.info(ZwiftInsiderVelocityMatrix_kph)
    logger.info("ZwiftInsiderVelocityMatrix_ms:")
    logger.info(ZwiftInsiderVelocityMatrix_ms)

    # # Create the velocity matrix with the same shape as ZwiftInsiderWattageMatrix
    velocity_matrix = np.tile(ZwiftInsiderVelocityMatrix_kph, (ZwiftInsiderWattageMatrix.shape[0], 1))
    logger.info("Velocity Matrix (km/h):")
    logger.info(velocity_matrix)

    # # Create the velocity matrix with the same shape as ZwiftInsiderWattageMatrix
    velocity_matrix = np.tile(ZwiftInsiderVelocityMatrix_ms, (ZwiftInsiderWattageMatrix.shape[0], 1))
    logger.info("Velocity Matrix (m/s):")
    logger.info(velocity_matrix)


if __name__ == "__main__":
    main()

