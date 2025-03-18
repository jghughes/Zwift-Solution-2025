from typing import List, Union, Dict 
from tabulate import tabulate

from formulae import *
from zwiftrider import ZwiftRiderItem


class ZwiftRiderCache:
    _cache: Dict[str, ZwiftRiderItem] = {}

    @classmethod
    def get_from_cache(cls, key: Union[str, None]) -> Union[ZwiftRiderItem, None]:
        if key is None:
            return None
        return cls._cache.get(key)

    @classmethod
    def add_to_cache(cls, key: Union[str, None], instance: ZwiftRiderItem):
        if key is None:
            return
        cls._cache[key] = instance

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache.clear()

    @classmethod
    def get_cache_contents(cls) -> Dict[str, ZwiftRiderItem]:
        return cls._cache

    @classmethod
    def display_cache_contents(cls) -> str:
        if not cls._cache:
            return "Cache is empty."
        
        cache_contents = ["Cache contents:"]
        for key, rider in cls._cache.items():
            cache_contents.append(f"Key: {key}")
            rider_attrs = [[attr, getattr(rider, attr)] for attr in rider.model_fields.keys()]
            cache_contents.append(tabulate(rider_attrs, tablefmt="plain"))
            cache_contents.append("")  # Add a blank line for readability


            # cache_contents.append(f"  ZwiftID: {rider.zwiftid}")
            # cache_contents.append(f"  Name: {rider.name}")
            # cache_contents.append(f"  Weight: {rider.weight}")
            # cache_contents.append(f"  Height: {rider.height}")
            # cache_contents.append(f"  Gender: {rider.gender.value}")
            # cache_contents.append(f"  FTP: {rider.ftp}")
            # cache_contents.append(f"  Zwift Racing Score: {rider.zwift_racing_score}")
            # cache_contents.append(f"  Velo Rating: {rider.velo_rating}")
            # cache_contents.append("")  # Add a blank line for readability
        
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
    import logging
    from jgh_logging import jgh_configure_logging
    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # example: Instantiate ZwiftRiderItem using the example from Config 
    # i.e.how we could do it from a JSON file
    example_data = ZwiftRiderItem.Config.json_schema_extra["johnh"]
    rider_john = ZwiftRiderItem.model_validate(example_data)


    # Test cache functionality
    logger.info("\nTesting cache functionality with rider_john")
    rider_john_key = rider_john.get_key()
    ZwiftRiderCache.add_to_cache(rider_john_key, rider_john)

    # Attempt to get_or_create rider_john again instantiated using get_or_create()
    # This should return the cached instance
    cached_rider_john = ZwiftRiderCache.get_or_create(
        zwiftid=rider_john.zwiftid,
        name=rider_john.name,
        weight=rider_john.weight,
        height=rider_john.height,
        gender=rider_john.gender,
        ftp=rider_john.ftp,
        zwift_racing_score=rider_john.zwift_racing_score,
        velo_rating=rider_john.velo_rating
    )

    # Check if the cached instance is the same as the original instance
    if cached_rider_john is rider_john:
        logger.info("\nCache is working: The second attempt to get_or_create rider_john returned the cached instance.")
    else:
        logger.error("\nCache is not working: The second attempt to get_or_create rider_john did not return the cached instance.")

    # Log the count of items in the cache
    cache_count = ZwiftRiderCache.get_cache_count()
    logger.info(f"Number of items in the cache: {cache_count}\n")

    # Display cache contents
    cache_contents = ZwiftRiderCache.display_cache_contents()
    logger.info("\nCache contents:")
    logger.info("\n" + cache_contents)






if __name__ == "__main__":
    main()
