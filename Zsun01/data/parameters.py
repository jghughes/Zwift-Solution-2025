import logging
from jgh_logging import jgh_configure_logging
import numpy as np

# Configure logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)


# Define the ZwiftInsiderWattageMatrix
ZwiftInsiderWattageMatrix = np.array([
    [300, 350, 400],
    [212, 252, 290],
    [196, 236, 261],
    [191, 217, 255]
])

# Define the ZwiftInsiderVelocityMatrix_kph (km/h)
ZwiftInsiderVelocityMatrix_kph = np.array([39.9, 42.2, 44.4])

