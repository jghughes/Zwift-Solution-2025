import numpy as np

def generate_cyclic_matrix(n : int):

    # Create the initial row
    first_row = np.array([f"rider{i+1}" for i in range(n)])
    
    # Generate the cyclic matrix using roll
    matrix = np.array([np.roll(first_row, -i) for i in range(n)])
    
    return matrix

# Example usage:
def main():
    # Configure logging
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    n = 6
    matrix = generate_cyclic_matrix(n)
    for row in matrix:
        logger.info(row)

if __name__ == "__main__":
    main()
