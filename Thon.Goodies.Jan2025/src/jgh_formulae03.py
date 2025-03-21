def generate_work_rider_mapping(n: int):
    """
    Generates a mapping of work riders to tasks.

    The row calculation is done as follows:
    - k: The current work rider index, starting from 1 up to n.
    - n: The total number of work riders/tasks.
    - j: The current task index, starting from 0 up to n-1.
    - k + n - j - 1: This expression adjusts the row index based on the current work rider and task.
      By subtracting j and adding n - 1, we effectively rotate the rows in the desired pattern.
    - % n: This modulo operation ensures that the row index wraps around when it exceeds n.
      For example, if n is 3, the row index will cycle through 1, 2, and 3.
    - + 1: This adjusts the 0-based index (resulting from the modulo operation) to a 1-based index,
      which matches the desired output format.

    This calculation ensures that the rows are rotated in such a way that they match the specified pattern:
    - For work_rider1, the rows are 1, 3, 2.
    - For work_rider2, the rows are 2, 1, 3.
    - For work_rider3, the rows are 3, 2, 1.

    Args:
        n (int): The number of work riders/tasks.

    Returns:
        dict: A dictionary mapping work riders to their respective tasks.
    """
    mapping = {}
    for k in range(1, n + 1):
        work_rider = []
        for j in range(n):
            row = (k + n - j - 1) % n + 1
            col = j + 1
            work_rider.append((f"p{row}", f"t{col}"))
        mapping[f"work_rider{k}"] = work_rider
    return mapping

# Example usage:
def main():
    # Configure logging
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    n = 3
    mapping = generate_work_rider_mapping(n)
    for rider, tasks in mapping.items():
        logger.info(f"{rider} = {tasks}")

if __name__ == "__main__":
    main()
