from typing import Union, Dict, TypeVar, Generic
from tabulate import tabulate

T = TypeVar('T')

class JghCache(Generic[T]):
    """
    A generic cache class for storing and retrieving objects of any type.

    This class provides methods to add, retrieve, and clear items in the cache.
    It also includes methods to get the count of items in the cache and to display
    the cache contents in a readable format.

    Attributes:
    _cache (Dict[str, T]): A dictionary to store cached items with string keys.

    Methods:
    get_from_cache(cls, key: Union[str, None]) -> Union[T, None]:
        Retrieves an item from the cache by its key.
    
    add_to_cache(cls, key: Union[str, None], instance: T):
        Adds an item to the cache with the specified key.
    
    clear_cache(cls) -> None:
        Clears all items from the cache.
    
    get_cache_contents(cls) -> Dict[str, T]:
        Returns the contents of the cache as a dictionary.
    
    display_cache_contents(cls) -> str:
        Returns a string representation of the cache contents in a readable format.
    
    get_cache_count(cls) -> int:
        Returns the count of items in the cache.
    """
    _cache: Dict[str, T] = {}

    @classmethod
    def get_from_cache(cls, key: Union[str, None]) -> Union[T, None]:
        """
        Retrieves an item from the cache by its key.

        Args:
        key (Union[str, None]): The key of the item to retrieve.

        Returns:
        Union[T, None]: The cached item if found, otherwise None.
        """
        if key is None:
            return None
        return cls._cache.get(key)

    @classmethod
    def add_to_cache(cls, key: Union[str, None], instance: T):
        """
        Adds an item to the cache with the specified key.

        Args:
        key (Union[str, None]): The key to associate with the item.
        instance (T): The item to cache.
        """
        if key is None:
            return
        cls._cache[key] = instance 

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clears all items from the cache.
        """
        cls._cache.clear()

    @classmethod
    def get_cache_contents(cls) -> Dict[str, T]:
        """
        Returns the contents of the cache as a dictionary.

        Returns:
        Dict[str, T]: The cache contents.
        """
        return cls._cache

    @classmethod
    def display_cache_contents(cls) -> str:
        """
        Returns a string representation of the cache contents in a readable format.

        Returns:
        str: A readable string representation of the cache contents.
        """
        if not cls._cache:
            return "Cache is empty."
        
        cache_contents = [""]
        for key, rider in cls._cache.items():
            cache_contents.append(f"Key: {key}")
            rider_attrs = [[attr, value] for attr, value in vars(rider).items()]
            cache_contents.append(tabulate(rider_attrs, tablefmt="plain"))
            cache_contents.append("")  # Add a blank line for readability
        
        return "\n".join(cache_contents)

    @classmethod
    def get_cache_count(cls) -> int:
        """
        Get the count of items in the cache.

        Returns:
        int: The number of items in the cache.
        """
        return len(cls._cache)

# Example usage
def main():
    from pydantic import BaseModel
    from typing import Optional
    import logging
    from jgh_logging import jgh_configure_logging

    # Define the AddressPydantic model
    class AddressPydantic(BaseModel):
        street: str
        city: str
        zipcode: Optional[str] = None

    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Create an instance of AddressPydantic
    address_john = AddressPydantic(street="123 Main St", city="Anytown", zipcode="12345")
    address_john_key = "john_address"

    # Test cache functionality - test duplicates are not added to the cache
    logger.info("\nTesting cache functionality with address_john")
    JghCache[AddressPydantic].add_to_cache(address_john_key, address_john)
    JghCache[AddressPydantic].add_to_cache(address_john_key, address_john)

    cached_address_john = JghCache[AddressPydantic].get_from_cache(address_john_key)

    # Check if the cached instance is the same as the original instance
    if cached_address_john is address_john:
        logger.info("\nCache is working: The second attempt to get_or_create address_john returned the cached instance.")
    else:
        logger.error("\nCache is not working: The second attempt to get_or_create address_john did not return the cached instance.")

    # Log the count of items in the cache - should be 1 not 2 because duplicates are prevented
    cache_count = JghCache[AddressPydantic].get_cache_count()
    logger.info(f"Number of items in the cache: {cache_count}")

    # Display cache contents
    cache_contents = JghCache.display_cache_contents()
    logger.info("\nCache contents:")
    logger.info(cache_contents)

    # Create another instance of AddressPydantic
    address_mark = AddressPydantic(street="456 Elm St", city="Othertown", zipcode="67890")
    address_mark_key = "mark_address"

    logger.info("\nTesting cache functionality with addition of address_mark")
    JghCache[AddressPydantic].add_to_cache(address_mark_key, address_mark)

    # Log the count of items in the cache - should be 2
    cache_count = JghCache[AddressPydantic].get_cache_count()
    logger.info(f"Number of items in the cache: {cache_count}\n")

    # Display cache contents
    cache_contents = JghCache.display_cache_contents()
    logger.info("\nCache contents:")
    logger.info(cache_contents)




if __name__ == "__main__":
    main()
