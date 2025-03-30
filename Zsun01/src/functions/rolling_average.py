from typing import  List

def calculate_rolling_averages(numbers: List[float], window_size: int) -> List[float]:
    """
    Calculate the rolling average of the given numbers with the specified window size.

    This function computes the rolling average for a list of numbers using a 
    specified window size. The window size determines the number of consecutive 
    numbers to include in each average calculation. We assume that the length of 
    the input list `numbers` is small, potentially as small as three items. Given 
    this assumption, the function is implemented in a straightforward manner 
    without complex optimizations.

    Args:
        numbers (List[float]): The list of numbers for which the rolling average 
        is to be calculated.
        window_size (int): The size of the rolling window, i.e., the number of 
        consecutive numbers to include in each average calculation.

    Returns:
        List[float]: The list of rolling average numbers. Each value in the 
        returned list represents the average of a subset of the input numbers, 
        with the subset size determined by the window size. The length of the 
        returned list will be `len(numbers) - window_size + 1`.

    Example:
        >>> numbers = [1, 2, 3, 4, 5]
        >>> window_size = 3
        >>> calculate_rolling_averages(numbers, window_size)
        [2.0, 3.0, 4.0]

    In this example, the rolling average is calculated for a window size of 3. 
    The first value in the returned list is the average of the first three numbers 
    in the input list (1, 2, 3), the second value is the average of the next 
    three numbers (2, 3, 4), and so on.

    Handling small input lists:
    - If the length of `numbers` is less than the `window_size`, the function will 
    return an empty list.
    - The function iterates over the input list and calculates the average for 
    each window of the specified size.
    """
    if not numbers or window_size <= 0:
        return []

    rolling_averages: List[float] = []
    for i in range(len(numbers) - window_size + 1):
        window = numbers[i:i + window_size]
        rolling_averages.append(sum(window) / window_size)

    return rolling_averages

