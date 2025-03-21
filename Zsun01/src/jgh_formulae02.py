from typing import List
from zwiftrider_item import ZwiftRiderItem

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
    # Configure logging
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from typing import Dict
    from jgh_read_write import read_text
    from jgh_serialization import JghSerialization
    from zwiftrider_dto import ZwiftRiderDataTransferObject



    # Load rider data from JSON
    inputjson = read_text("C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/", "rider_dictionary.json")
    dict_of_zwiftrider_dto= JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDataTransferObject])

    #transform to ZwiftRiderItem dict
    dict_of_zwiftrideritem = ZwiftRiderItem.from_dataTransferObject_dict(dict_of_zwiftrider_dto)

    # Instantiate ZwiftRiderItem objects for barryb, johnh, and lynseys
    barryb = dict_of_zwiftrideritem['barryb']
    johnh = dict_of_zwiftrideritem['johnh']
    lynseys = dict_of_zwiftrideritem['lynseys']

    # Create a list of the selected riders
    riders = [barryb, johnh, lynseys]

    # Generate a cyclic matrix for the list of riders
    matrix = generate_cyclic_matrix(riders)

    # Display the matrix by rider name
    for row in matrix:
        logger.info([rider.name for rider in row])

if __name__ == "__main__":
    main()
