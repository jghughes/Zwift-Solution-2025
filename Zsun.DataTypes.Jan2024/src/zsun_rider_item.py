from dataclasses import dataclass,  asdict
from typing import Optional
import numpy as np
from zsun_rider_dto import ZsunRiderDTO 
from jgh_formulae import estimate_speed_from_wattage, estimate_watts_from_speed, estimate_power_factor_in_peloton
from jgh_power_curve_fit_models import decay_model_numpy

@dataclass(frozen=True, eq=True)  # immutable and hashable, we use this as a dictionary key everywhere
class ZsunRiderItem:
    """
    A frozen data class representing a Zwift rider.
    Can be used as a cache key or dictionary key, or in a set.
    """

    zwift_id                   : str   = ""    # Zwift ID of the rider
    name                       : str   = ""    # Name of the rider
    weight_kg                  : float = 0.0   # Weight of the rider in kilograms
    height_cm                  : float = 0.0   # Height of the rider in centimeters
    gender                     : str   = ""    # Gender of the rider
    age_years                  : float = 0.0   # Age of the rider in years
    agegroup                   : str   = ""    # Age group of the rider
    zwift_zftp                 : float = 0.0   # Functional Threshold Power in watts
    zwift_zrs                  : float   = 0.0     # Zwift racing score
    zwift_cat                  : str   = ""    # A+, A, B, C, D, E
    velo_score                 : float = 0.0   # Velo score typically over 1000
    velo_cat_num               : int   = 0     # Velo rating 1 to 10
    velo_cat_name              : str   = ""    # Copper, Silver, Gold etc
    velo_cp                    : float = 0.0   # Critical power in watts
    velo_awc                   : float = 0.0   # Anaerobic work capacity in kilojoules
    jgh_pull_adjustment_watts  : float = 0.0   # Adjustment watts for pulling
    jgh_cp                     : float = 0.0   # Critical power in watts
    jgh_w_prime                : float = 0.0   # Critical power W' in kilojoules
    jgh_ftp_curve_coefficient  : float = 0.0   # Coefficient for FTP modeling
    jgh_ftp_curve_exponent     : float = 0.0   # Exponent for FTP modeling
    jgh_pull_curve_coefficient : float = 0.0   # Coefficient for pull modeling
    jgh_pull_curve_exponent    : float = 0.0   # Exponent for pull modeling
    jgh_when_curves_fitted     : str   = ""    # Timestamp indicating when the models were fitted
    
    class Config:
        # Define the extra JSON schema for the class in the form of a dictionary of riders
        json_schema_extra = {
            "davek": {
                "zwift_id": "3147366",
                "name": "Dave K",
                "weight_kg": 73.4,
                "height_cm": 182,
                "gender": "m",
                "zwift_zftp": 276,
                "zwift_zrs": 744,
                "velo_cat_num": 1897,
            },
            "huskyc": {
                "zwift_id": "5134",
                "name": "Husky C",
                "weight_kg": 75.5,
                "height_cm": 178,
                "gender": "m",
                "zwift_zftp": 268,
                "zwift_zrs": 552,
                "velo_cat_num": 1519,
            },
            "scottm": {
                "zwift_id": "11526",
                "name": "Scott M",
                "weight_kg": 78,
                "height_cm": 165,
                "gender": "m",
                "zwift_zftp": 247,
                "zwift_zrs": 509,
                "velo_cat_num": 1537,
            },
            "johnh": {
                "zwift_id": "1884456",
                "name": "John H",
                "weight_kg": 75.4,
                "height_cm": 174,
                "gender": "m",
                "zwift_zftp": 233,
                "zwift_zrs": 351,
                "velo_cat_num": 1067,
            },
            "joshn": {
                "zwift_id": "2508033",
                "name": "Josh N",
                "weight_kg": 101,
                "height_cm": 178,
                "gender": "m",
                "zwift_zftp": 260,
                "zwift_zrs": 285,
                "velo_cat_num": 942,
            },
        }

    @staticmethod
    def create(zwiftid: str, name: str, weight_kg: float, height_cm: float, gender: str, 
        zwift_zftp: float, zwift_zrs: int, velo_cat_num: int
    ) -> 'ZsunRiderItem':
        """
        Create a ZsunRiderItem instance with the given parameters

        Args:
           zwift_id            (int)  : The Zwift ID of the rider.
            name               (str)  : The name of the rider.
            weight_kg             (float): The weight_kg of the rider in kilograms.
            height_cm             (float): The height_cm of the rider in centimeters.
            gender             (Gender): The gender of the rider.
            zwift_zftp                (float): Functional Threshold Power in watts.
            zwift_zrs (int)  : Zwift racing score.
            velo_cat_num        (int)  : Velo rating.
    
        Returns:
            ZsunRiderItem: A ZsunRiderItem instance with the given parameters.
        """

        instance = ZsunRiderItem(
            zwift_id=zwiftid,
            name=name,
            weight_kg=weight_kg,
            height_cm=height_cm,
            gender=gender,
            zwift_zftp=zwift_zftp,
            zwift_zrs=zwift_zrs,
            velo_cat_num=velo_cat_num
        )

        return instance

    def calculate_strength(self) -> float:
        return self.zwift_zrs

    def calculate_kph_riding_alone(self, power: float) -> float:
        """
        Estimate the speed (km/h) given the power (wattage), weight_kg (kg), and 
        height_cm (cm) using the Newton-Raphson method.

        Args:
        power (float): The power in watts.

        Returns:
        float: The estimated speed in km/h.
        """
        # Estimate the speed in km/h using the estimate_speed_from_wattage function
        speed_kph = estimate_speed_from_wattage(power, self.weight_kg, self.height_cm)
        return speed_kph

    def calculate_wattage_riding_alone(self, speed: float) -> float:
        """
        Calculate the power (P) as a function of speed (km/h), weight_kg (kg), and 
        height_cm (cm).

        Args:
        speed (float): The speed in km/h.

        Returns:
        float: The calculated power in watts.
        """
        # Calculate the power using the estimate_watts_from_speed function
        power = estimate_watts_from_speed(speed, self.weight_kg, self.height_cm)
        return power

    def calculate_wattage_riding_in_the_peloton(
        self, speed: float, position: int
    ) -> float:
        """
        Calculate the wattage required for a rider given their speed and position 
        in the peloton.

        Args:
        rider (ZsunRiderItem): The rider object.
        speed (float): The speed in km/h.
        position (int): The position in the peloton.

        Returns:
        float: The required wattage in watts.
        """
        # Calculate the base power required for the given speed
        base_power = self.calculate_wattage_riding_alone(speed)

        # Get the power factor based on the rider's position in the peloton
        power_factor = estimate_power_factor_in_peloton(position)

        # Adjust the power based on the power factor
        adjusted_power = base_power * power_factor

        return round(adjusted_power, 3)

    def calculate_speed_riding_in_the_peloton(
        self, power: float, position: int
    ) -> float:
        """
        Calculate the speed (km/h) for a rider given their power output (watts) 
        and position in the peloton.

        Args:
        power (float): The power output in watts.
        position (int): The position in the peloton.

        Returns:
        float: The estimated speed in km/h.
        """
        # Get the power factor based on the rider's position in the peloton
        power_factor = estimate_power_factor_in_peloton(position)

        # Adjust the power based on the power factor
        adjusted_watts = power / power_factor

        # Estimate the speed in km/h using the estimate_speed_from_wattage function
        speed_kph = estimate_speed_from_wattage(adjusted_watts, self.weight_kg, self.height_cm)
        
        return round(speed_kph, 3)

    def get_critical_power_watts(self) -> float:
        return self.jgh_cp

    def get_anaerobic_work_capacity_kj(self) -> float:
        return self.jgh_w_prime / 1_000.0

    def get_30sec_watts(self) -> float:

        pull_short = decay_model_numpy(np.array([300]), self.jgh_pull_curve_coefficient, self.jgh_pull_curve_exponent)

        answer =  pull_short[0] + self.jgh_pull_adjustment_watts

        return answer

    def get_1_minute_watts(self) -> float:

        pull_medium = decay_model_numpy(np.array([600]), self.jgh_pull_curve_coefficient, self.jgh_pull_curve_exponent)

        answer =  pull_medium[0] + self.jgh_pull_adjustment_watts

        return answer

    def get_2_minute_watts(self) -> float:

        pull_long = decay_model_numpy(np.array([1200]), self.jgh_pull_curve_coefficient, self.jgh_pull_curve_exponent)

        answer =  pull_long[0] + self.jgh_pull_adjustment_watts

        return answer

    def get_3_minute_watts(self) -> float:

        # same as 2 minute because this is for beasts who can withstand more time at the front 
        # at the same power
        pull_long = decay_model_numpy(np.array([1200]), self.jgh_pull_curve_coefficient, self.jgh_pull_curve_exponent)

        answer =  pull_long[0] + self.jgh_pull_adjustment_watts

        return answer

    def get_ftp_60_minute_watts(self) -> float:

        ftp = decay_model_numpy(np.array([3_600]), self.jgh_ftp_curve_coefficient, self.jgh_ftp_curve_exponent)

        answer =  ftp[0]

        return answer

    def get_when_models_fitted(self) -> str:
        return self.jgh_when_curves_fitted

    @staticmethod
    def to_dataTransferObject(item: Optional["ZsunRiderItem"]) -> ZsunRiderDTO:
        if item is None:
            return ZsunRiderDTO()
        return ZsunRiderDTO(
            zwift_id                   = item.zwift_id,
            name                       = item.name,
            weight_kg                  = item.weight_kg,
            height_cm                  = item.height_cm,
            gender                     = item.gender,
            age_years                  = item.age_years,
            agegroup                   = item.agegroup,
            zwift_zftp                 = item.zwift_zftp,
            zwift_zrs                  = item.zwift_zrs,
            zwift_cat                  = item.zwift_cat,
            velo_score             = item.velo_score,
            velo_cat_num                = item.velo_cat_num,
            velo_cat_name               = item.velo_cat_name,
            velo_cp                     = item.velo_cp,
            velo_awc                    = item.velo_awc,
            jgh_pull_adjustment_watts  = item.jgh_pull_adjustment_watts,
            jgh_cp                     = item.jgh_cp,
            jgh_w_prime                = item.jgh_w_prime,
            jgh_ftp_curve_coefficient  = item.jgh_ftp_curve_coefficient,
            jgh_ftp_curve_exponent     = item.jgh_ftp_curve_exponent,
            jgh_pull_curve_coefficient = item.jgh_pull_curve_coefficient,
            jgh_pull_curve_exponent    = item.jgh_pull_curve_exponent,
            jgh_when_curves_fitted     = item.jgh_when_curves_fitted
        )


    @staticmethod
    def from_dataTransferObject(dto: Optional[ZsunRiderDTO]) -> "ZsunRiderItem":
        if dto is None:
            return ZsunRiderItem()
        return ZsunRiderItem(
            zwift_id                   = dto.zwift_id or "",
            name                       = dto.name or "",
            weight_kg                  = dto.weight_kg or 0.0,
            height_cm                  = dto.height_cm or 0.0,
            gender                     = dto.gender or "",
            age_years                  = dto.age_years or 0.0,
            agegroup                   = dto.agegroup or "",
            zwift_zftp                 = dto.zwift_zftp or 0.0,
            zwift_zrs                  = dto.zwift_zrs or 0.0,
            zwift_cat                  = dto.zwift_cat or "",
            velo_score                 = dto.velo_score or 0.0,
            velo_cat_num               = dto.velo_cat_num or 0,
            velo_cat_name              = dto.velo_cat_name or "",
            velo_cp                    = dto.velo_cp or 0.0,
            velo_awc                   = dto.velo_awc or 0.0,
            jgh_pull_adjustment_watts  = dto.jgh_pull_adjustment_watts or 0.0,
            jgh_cp                     = dto.jgh_cp or 0.0,
            jgh_w_prime                = dto.jgh_w_prime or 0.0,
            jgh_ftp_curve_coefficient  = dto.jgh_ftp_curve_coefficient or 0.0,
            jgh_ftp_curve_exponent     = dto.jgh_ftp_curve_exponent or 0.0,
            jgh_pull_curve_coefficient = dto.jgh_pull_curve_coefficient or 0.0,
            jgh_pull_curve_exponent    = dto.jgh_pull_curve_exponent or 0.0,
            jgh_when_curves_fitted     = dto.jgh_when_curves_fitted or ""
        )



def main():

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from tabulate import tabulate
    from typing import List, Union

    # # example: Instantiate ZsunRiderItem using the example from Config 
    # # i.e.how we could do it from a JSON file
    example_data = ZsunRiderItem.Config.json_schema_extra["johnh"]
    example_rider = ZsunRiderDTO.model_validate(example_data)
    rider1 = ZsunRiderItem.from_dataTransferObject(example_rider)

    # Log the instantiated object using a table
    rider_attrs = asdict(rider1)    
    logger.info("\nZwiftRider instantiated (ctor) from JSON config is:")
    logger.info("\n" + tabulate(rider_attrs.items(), tablefmt="plain"))

    # example : instantiate examples of two riders of differing ability. for each of them 
    # calculate wattage at a given speed (40kph)and in two positions in the peloton - 
    # position 1 and position 5. tabulate the results in a table and log it.
    example_data = ZsunRiderItem.Config.json_schema_extra["davek"]
    example_rider = ZsunRiderDTO.model_validate(example_data)
    rider2 = ZsunRiderItem.from_dataTransferObject(example_rider)

    riders = [rider1, rider2]
    table: List[List[Union[str, float]]] = []
    headers = [
        "Rider", "Wattage (P 1, 40 km/h)", 
        "Wattage (P 5, 40 km/h)"
    ]
    for rider in riders:
        row : List[Union[str, float]] = [rider.name]
        for position in [1, 5]:
            wattage = rider.calculate_wattage_riding_in_the_peloton(40, position)
            row.append(str(wattage))  # Convert wattage to string
        table.append(row)
    
    # Log the table
    logger.info("\nRider wattage in positions 1 and 5 for 40 km/h")
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))

    # example : using rider "John H" instantiated using ctor
    # calculate wattage for each position in the peloton from 1 to 5
    # at a given speed (40kph) and tabulate neatly and log it.
    rider_john = rider1

    positions = range(1, 6)
    table: List[List[Union[str, float]]] = []
    headers = ["Position", "Wattage (40 km/h)"]

    for position in positions:
        wattage = rider_john.calculate_wattage_riding_in_the_peloton(40, position)
        table.append([position, wattage])

    # Log the table
    logger.info("\nWattage for John H in positions 1 to 5 at 40 km/h")
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))

    # example : using rider "John H" instantiated using ctor (no cache)
    # calculate speed for each position in the peloton from 1 to 5
    # at a given wattage (zwift_zftp=233) and tabulate neatly and log it.
    rider_john = ZsunRiderItem(
        name=rider1.name, weight_kg=rider1.weight_kg, height_cm=rider1.height_cm, zwift_zftp=rider1.zwift_zftp, gender=rider1.gender, velo_cat_num=rider1.velo_cat_num)

    positions = range(1, 6)
    table: List[List[Union[str, float]]] = []
    headers = ["Position", f"Speed (km/h) at FTP {rider_john.zwift_zftp}"]

    for position in positions:
        # Calculate the speed for the given position and FTP
        speed = rider_john.calculate_speed_riding_in_the_peloton(rider_john.zwift_zftp, position)
        table.append([position, speed])

    # Log the table
    logger.info(f"\nSpeed for John H in positions 1 to 5 at FTP {rider_john.zwift_zftp}")
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))


if __name__ == "__main__":
    main()
