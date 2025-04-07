from typing import List
from zwiftrider_related_items import ZwiftRiderItem

#   this is not used anywhere. it is a method to test the cyclic formula used 
#   for determining the order of riders in a rotating paceline.
#   see populate_rider_work_assignments() in jgh_formulae04.py

def generate_cyclic_matrix(riders: List[ZwiftRiderItem]) -> List[List[ZwiftRiderItem]]:
    """
    Generates a cyclic matrix where each column is a cyclic permutation of the first column.

    Args:
        riders (List[ZwiftRiderItem]): A list of ZwiftRiderItem objects.

    Returns:
        List[List[ZwiftRiderItem]]: A 2D list representing the cyclic matrix.

    The function uses the provided list of ZwiftRiderItem objects to create the initial column.
    It then generates each subsequent column by cyclically shifting the elements of the initial column.
    For example, if the list of riders contains ZwiftRiderItem objects (with names) 
    ['Barry B', 'John H', 'Lynsey S'], the resulting matrix will be:

    [
        ['Barry B', 'John H', 'Lynsey S']
        ['John H', 'Lynsey S', 'Barry B']
        ['Lynsey S', 'Barry B', 'John H']
    ]
    """
    n = len(riders)
    
    # Generate the cyclic matrix using simple iteration
    matrix: List[List[ZwiftRiderItem]] = []
    for i in range(n):
        row = [riders[(i + j) % n] for j in range(n)]
        matrix.append(row)
    
    return matrix

# Example usage:
def main():
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from handy_utilities import get_all_zwiftriders

    dict_of_zwiftrideritem = get_all_zwiftriders()

    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['5490373'] # barryb
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['58160'] # johnh
    lynseys : ZwiftRiderItem = dict_of_zwiftrideritem['383480'] # lynseys

    riders = [barryb, johnh, lynseys]

    matrix = generate_cyclic_matrix(riders)

    for row in matrix:
        logger.info([rider.name for rider in row])

if __name__ == "__main__":
    main()
