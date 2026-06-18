from typing import List
from rider_compute_item import RiderComputeItem

#   this is not used anywhere. it is a method to test the cyclic formula used 
#   for determining the order of riders in a rotating paceline.
#   see populate_rider_work_assignments() in jgh_formulae04.py

def generate_cyclic_matrix(riders: List[RiderComputeItem]) -> List[List[RiderComputeItem]]:
    """
    Generates a cyclic matrix where each column is a cyclic permutation of the first_name column.

    Args:
        riders (List[RiderComputeItem]): A list of RiderComputeItem objects.

    Returns:
        List[List[RiderComputeItem]]: A 2D list representing the cyclic matrix.

    The function uses the provided list of RiderComputeItem objects to create the initial column.
    It then generates each subsequent column by cyclically shifting the elements of the initial column.
    For example, if the list of riders contains RiderComputeItem objects (with names) 
    ['Barry B', 'John H', 'Lynsey S'], the resulting matrix will be:

    [
        ['Barry B', 'John H', 'Lynsey S']
        ['John H', 'Lynsey S', 'Barry B']
        ['Lynsey S', 'Barry B', 'John H']
    ]
    """
    n = len(riders)
    
    # Generate the cyclic matrix using simple iteration
    matrix: List[List[RiderComputeItem]] = []
    for i in range(n):
        row = [riders[(i + j) % n] for j in range(n)]
        matrix.append(row)
    
    return matrix

