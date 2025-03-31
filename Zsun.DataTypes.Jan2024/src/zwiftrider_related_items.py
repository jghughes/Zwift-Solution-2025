from typing import Dict
from enum import Enum
from dataclasses import dataclass
from dataclasses import dataclass, field, asdict
from zwiftrider_dto import ZwiftRiderDataTransferObject
from zwiftrider_cp_dto import ZwiftRiderCriticalPowerDataTransferObject

from jgh_formulae import estimate_speed_from_wattage, estimate_watts_from_speed, estimate_power_factor_in_peloton


class Gender(Enum):
    MALE = 'm'
    FEMALE = 'f'

    @classmethod
    def _missing_(cls, value : object):
        """
        Return the default value 'MALE' if the provided value is None or invalid.
        """
        if value is None:
            return cls.MALE
        return super()._missing_(value)


@dataclass(frozen=True, eq=True) # immutable and hashable
class ZwiftRiderItem():
    """
    A frozen data class representing a Zwift rider.
    Can be used as a cache key or dictionary key, or in a set.

    Attributes:
        zwiftid            : int    The Zwift ID of the rider.
        name               : str    The name of the rider.
        weight             : float  The weight of the rider in kilograms.
        height             : float  The height of the rider in centimeters.
        gender             : Gender The gender of the rider.
        ftp                : float  Functional Threshold Power in watts.
        zwift_racing_score : int    Zwift racing score.
        velo_rating        : int    Velo rating.

    Methods:
        make_identifier(
            zwiftid: int, name: str, weight: float, height: float, gender: Gender, 
            ftp: float, zwift_racing_score: int, velo_rating: int
        ) -> str:
            Generate a unique key based on all the parameters that define
            an instance of the class as used in the ctor for the frozen class.

        get_identifier() -> str:
            Generate a unique key for the current ZwiftRiderItem instance.

        calculate_strength() -> float:
            Calculate the strength of the rider based on FTP and weight.

        calculate_kph_riding_alone(power: float) -> float:
            Estimate the speed (km/h) given the power (wattage), weight (kg), and height (cm) using the Newton-Raphson method.

        calculate_wattage_riding_alone(speed: float) -> float:
            Calculate the power (P) as a function of speed (km/h), weight (kg), and height (cm).

        calculate_wattage_riding_in_the_peloton(speed: float, position: int) -> float:
            Calculate the wattage required for a rider given their speed and position in the peloton.

        calculate_speed_riding_in_the_peloton(power: float, position: int) -> float:
            Calculate the speed (km/h) for a rider given their power output (watts) and position in the peloton.
    """    
    
    zwiftid            : int    = 0             # Zwift ID of the rider
    name               : str    = ""            # Name of the rider
    weight             : float  = 0             # Weight of the rider in kilograms
    height             : float  = 0             # Height of the rider in centimeters
    gender             : Gender = Gender.MALE   # Gender of the rider
    ftp                : float  = 0             # Functional Threshold Power in watts
    zwift_racing_score : int    = 0             # Zwift racing score
    velo_rating        : int    = 0             # Velo rating

    class Config:
        # Define the extra JSON schema for the class in the form of a dictionary of riders
        json_schema_extra = {
            "davek": {
                "zwiftid": 3147366,
                "name": "Dave K",
                "weight": 73.4,
                "height": 182,
                "gender": "m",
                "ftp": 276,
                "zwift_racing_score": 744,
                "velo_rating": 1897,
            },
            "huskyc": {
                "zwiftid": 5134,
                "name": "Husky C",
                "weight": 75.5,
                "height": 178,
                "gender": "m",
                "ftp": 268,
                "zwift_racing_score": 552,
                "velo_rating": 1519,
            },
            "scottm": {
                "zwiftid": 11526,
                "name": "Scott M",
                "weight": 78,
                "height": 165,
                "gender": "m",
                "ftp": 247,
                "zwift_racing_score": 509,
                "velo_rating": 1537,
            },
            "markb": {
                "zwiftid": 5530045,
                "name": "Mark B",
                "weight": 91.6,
                "height": 185,
                "gender": "m",
                "ftp": 229,
                "zwift_racing_score": 493,
                "velo_rating": 1309,
            },
            "barryb": {
                "zwiftid": 5490373,
                "name": "Barry B",
                "weight": 77,
                "height": 176,
                "gender": "m",
                "ftp": 273,
                "zwift_racing_score": 444,
                "velo_rating": 1294,
            },
            "johnh": {
                "zwiftid": 58160,
                "name": "John H",
                "weight": 75.4,
                "height": 174,
                "gender": "m",
                "ftp": 233,
                "zwift_racing_score": 351,
                "velo_rating": 1067,
            },
            "brenth": {
                "zwiftid": 480698,
                "name": "Brent H",
                "weight": 75.6,
                "height": 180,
                "gender": "m",
                "ftp": 243,
                "zwift_racing_score": 335,
                "velo_rating": 1078,
            },
            "joshn": {
                "zwiftid": 2508033,
                "name": "Josh N",
                "weight": 101,
                "height": 178,
                "gender": "m",
                "ftp": 260,
                "zwift_racing_score": 285,
                "velo_rating": 942,
            },
            "edh": {
                "zwiftid": 1713736,
                "name": "Ed H",
                "weight": 107.5,
                "height": 188,
                "gender": "m",
                "ftp": 274,
                "zwift_racing_score": 206,
                "velo_rating": 748,
            },
            "richardm": {
                "zwiftid": 1193,
                "name": "Richard M",
                "weight": 93,
                "height": 178,
                "gender": "m",
                "ftp": 200,
                "zwift_racing_score": 189,
                "velo_rating": 628,
            },
            "selenas": {
                "zwiftid": 2682791,
                "name": "Selena S",
                "weight": 63,
                "height": 171,
                "gender": "f",
                "ftp": 214,
                "zwift_racing_score": 345,
                "velo_rating": 1129,
            },
            "kristend": {
                "zwiftid": 2398312,
                "name": "Kristen D",
                "weight": 71.2,
                "height": 178,
                "gender": "f",
                "ftp": 236,
                "zwift_racing_score": 338,
                "velo_rating": 1035,
            },
            "lynseys": {
                "zwiftid": 383480,
                "name": "Lynsey S",
                "weight": 63.5,
                "height": 165,
                "gender": "f",
                "ftp": 201,
                "zwift_racing_score": 327,
                "velo_rating": 915,
            }
        }

    @staticmethod
    def create(zwiftid: int, name: str, weight: float, height: float, gender: Gender, 
        ftp: float, zwift_racing_score: int, velo_rating: int
    ) -> 'ZwiftRiderItem':
        """
        Create a ZwiftRiderItem instance with the given parameters

        Args:
            zwiftid (int): The Zwift ID of the rider.
            name (str): The name of the rider.
            weight (float): The weight of the rider in kilograms.
            height (float): The height of the rider in centimeters.
            gender (Gender): The gender of the rider.
            ftp (float): Functional Threshold Power in watts.
            zwift_racing_score (int): Zwift racing score.
            velo_rating (int): Velo rating.

        Returns:
            ZwiftRiderItem: A ZwiftRiderItem instance with the given parameters.
        """

        instance = ZwiftRiderItem(
            zwiftid=zwiftid,
            name=name,
            weight=weight,
            height=height,
            gender=gender,
            ftp=ftp,
            zwift_racing_score=zwift_racing_score,
            velo_rating=velo_rating
        )

        return instance

    def calculate_strength(self) -> float:
        return self.zwift_racing_score

    def calculate_kph_riding_alone(self, power: float) -> float:
        """
        Estimate the speed (km/h) given the power (wattage), weight (kg), and 
        height (cm) using the Newton-Raphson method.

        Args:
        power (float): The power in watts.

        Returns:
        float: The estimated speed in km/h.
        """
        # Estimate the speed in km/h using the estimate_speed_from_wattage function
        speed_kph = estimate_speed_from_wattage(power, self.weight, self.height)
        return speed_kph

    def calculate_wattage_riding_alone(self, speed: float) -> float:
        """
        Calculate the power (P) as a function of speed (km/h), weight (kg), and 
        height (cm).

        Args:
        speed (float): The speed in km/h.

        Returns:
        float: The calculated power in watts.
        """
        # Calculate the power using the estimate_watts_from_speed function
        power = estimate_watts_from_speed(speed, self.weight, self.height)
        return power

    def calculate_wattage_riding_in_the_peloton(
        self, speed: float, position: int
    ) -> float:
        """
        Calculate the wattage required for a rider given their speed and position 
        in the peloton.

        Args:
        rider (ZwiftRiderItem): The rider object.
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
        speed_kph = estimate_speed_from_wattage(adjusted_watts, self.weight, self.height)
        
        return round(speed_kph, 3)

    @staticmethod
    def to_dataTransferObject(item: "ZwiftRiderItem") -> ZwiftRiderDataTransferObject:
        """
        Convert a ZwiftRiderItem instance to a ZwiftRiderDataTransferObject.

        Args:
            item (ZwiftRiderItem): The ZwiftRiderItem instance to convert.

        Returns:
            ZwiftRiderDataTransferObject: The corresponding data transfer object.
        """
        return ZwiftRiderDataTransferObject(
            zwiftid=item.zwiftid,
            name=item.name,
            weight=item.weight,
            height=item.height,
            gender=item.gender.value,
            ftp=item.ftp,
            zwift_racing_score=item.zwift_racing_score,
            velo_rating=item.velo_rating
        )

    @staticmethod
    def from_dataTransferObject(dto: ZwiftRiderDataTransferObject) -> "ZwiftRiderItem":
        """
        Create a ZwiftRiderItem instance from a ZwiftRiderDataTransferObject.

        Args:
            dto (ZwiftRiderDataTransferObject): The data transfer object to convert.

        Returns:
            ZwiftRiderItem: The corresponding ZwiftRiderItem instance.
        """
        return ZwiftRiderItem(
            zwiftid=dto.zwiftid or 0,
            name=dto.name or "",
            weight=dto.weight or 0,
            height=dto.height or 0,
            gender=Gender(dto.gender) or 0,
            ftp=dto.ftp or 0,
            zwift_racing_score=dto.zwift_racing_score or 0,
            velo_rating=dto.velo_rating or 0
        )

    @staticmethod
    def from_dict_of_dataTransferObjects(dict_of_zwiftrider_dto: Dict[str, ZwiftRiderDataTransferObject]) -> Dict[str, 'ZwiftRiderItem']:
        """
        Transform a dictionary of ZwiftRiderDataTransferObject to a dictionary of ZwiftRiderItem.

        Args:
            dict_of_zwiftrider_dto (Dict[str, ZwiftRiderDataTransferObject]): The input dictionary.

        Returns:
            Dict[str, ZwiftRiderItem]: The transformed dictionary.
        """
        dict_of_zwiftrideritem = {
            key: ZwiftRiderItem.from_dataTransferObject(dto)
            for key, dto in dict_of_zwiftrider_dto.items()
        }
        return dict_of_zwiftrideritem# Example usage

@dataclass
class CriticalPowerItem:
    """
    A data class representing a zwiftrider's critical power data.
    
    Attributes:
        cpw_5_sec : float  Critical power for 5 seconds.
        cpw_15_sec: float  Critical power for 15 seconds.
        cpw_30_sec: float  Critical power for 30 seconds.
        cpw_1_min : float  Critical power for 1 minute.
        cpw_2_min : float  Critical power for 2 minutes.
        cpw_3_min : float  Critical power for 3 minutes.
        cpw_5_min : float  Critical power for 5 minutes.
        cpw_10_min: float  Critical power for 10 minutes.
        cpw_12_min: float  Critical power for 12 minutes.
        cpw_15_min: float  Critical power for 15 minutes.
        cpw_20_min: float  Critical power for 20 minutes.
        cpw_30_min: float  Critical power for 30 minutes.
        cpw_40_min: float  Critical power for 40 minutes.
    """
    cpw_5_sec : float  = 0.0
    cpw_15_sec: float  = 0.0
    cpw_30_sec: float  = 0.0
    cpw_1_min : float  = 0.0
    cpw_2_min : float  = 0.0
    cpw_3_min : float  = 0.0
    cpw_5_min : float  = 0.0
    cpw_10_min: float  = 0.0
    cpw_12_min: float  = 0.0
    cpw_15_min: float  = 0.0
    cpw_20_min: float  = 0.0
    cpw_30_min: float  = 0.0
    cpw_40_min: float  = 0.0
    cp: float = 0.0
    w_prime: float = 0.0


@dataclass
class RiderCriticalPowerItem:
    """
    A data class representing a zwiftrider's critical power data.
    The object can be converted to and from a data transfer object (DTO).

    Attributes:
        zwiftid   : int    The Zwift ID of the rider.
        name      : str    The name of the rider.
        cp: CriticalPowerItem  The critical power curve data.
    """

    zwiftid: int = 0
    name: str = ""
    cp: CriticalPowerItem = field(default_factory=CriticalPowerItem)

    class Config:
        # Define the extra JSON schema for the class in the form of a dictionary of riders' power curve items
        json_schema_extra = {
            "davek": {
                "zwiftid": 3147366,
                "name": "DaveK",
                "cp": {
                    "cpw_5_sec": 0.0,
                    "cpw_15_sec": 0.0,
                    "cpw_30_sec": 0.0,
                    "cpw_1_min": 0.0,
                    "cpw_2_min": 0.0,
                    "cpw_3_min": 0.0,
                    "cpw_5_min": 0.0,
                    "cpw_10_min": 0.0,
                    "cpw_12_min": 0.0,
                    "cpw_15_min": 0.0,
                    "cpw_20_min": 0.0,
                    "cpw_30_min": 0.0,
                    "cpw_40_min": 0.0,
                },
            },
            "timr": {
                "zwiftid": 5421258,
                "name": "TimR",
                "cp": {
                    "cpw_5_sec": 0.0,
                    "cpw_15_sec": 0.0,
                    "cpw_30_sec": 0.0,
                    "cpw_1_min": 0.0,
                    "cpw_2_min": 0.0,
                    "cpw_3_min": 0.0,
                    "cpw_5_min": 0.0,
                    "cpw_10_min": 0.0,
                    "cpw_12_min": 0.0,
                    "cpw_15_min": 0.0,
                    "cpw_20_min": 0.0,
                    "cpw_30_min": 0.0,
                    "cpw_40_min": 0.0,
                },
            },
            "johnh": {
                "zwiftid": 58160,
                "name": "JohnH",
                "cp": {
                    "cpw_5_sec": 546,
                    "cpw_15_sec": 434,
                    "cpw_30_sec": 425,
                    "cpw_1_min": 348,
                    "cpw_2_min": 0,
                    "cpw_3_min": 293,
                    "cpw_5_min": 292,
                    "cpw_10_min": 268,
                    "cpw_12_min": 264,
                    "cpw_15_min": 254,
                    "cpw_20_min": 254,
                    "cpw_30_min": 252,
                    "cpw_40_min": 244,
                },
            },
        }

    @staticmethod
    def to_dataTransferObject(item: "RiderCriticalPowerItem",) -> ZwiftRiderCriticalPowerDataTransferObject:

        answer = ZwiftRiderCriticalPowerDataTransferObject(
            zwiftid=item.zwiftid,
            name=item.name,
            cpw_5_sec=item.cp.cpw_5_sec,
            cpw_15_sec=item.cp.cpw_15_sec,
            cpw_30_sec=item.cp.cpw_30_sec,
            cpw_1_min=item.cp.cpw_1_min,
            cpw_2_min=item.cp.cpw_2_min,
            cpw_3_min=item.cp.cpw_3_min,
            cpw_5_min=item.cp.cpw_5_min,
            cpw_10_min=item.cp.cpw_10_min,
            cpw_12_min=item.cp.cpw_12_min,
            cpw_15_min=item.cp.cpw_15_min,
            cpw_20_min=item.cp.cpw_20_min,
            cpw_30_min=item.cp.cpw_30_min,
            cpw_40_min=item.cp.cpw_40_min,
        )
        return answer

    @staticmethod
    def from_dataTransferObject(dto: ZwiftRiderCriticalPowerDataTransferObject) -> "RiderCriticalPowerItem":
        answer = RiderCriticalPowerItem(zwiftid=dto.zwiftid or 0, name=dto.name or "",  cp=CriticalPowerItem(
                cpw_5_sec=dto.cpw_5_sec or 0.0,
                cpw_15_sec=dto.cpw_15_sec or 0.0,
                cpw_30_sec=dto.cpw_30_sec or 0.0,
                cpw_1_min=dto.cpw_1_min or 0.0,
                cpw_2_min=dto.cpw_2_min or 0.0,
                cpw_3_min=dto.cpw_3_min or 0.0,
                cpw_5_min=dto.cpw_5_min or 0.0,
                cpw_10_min=dto.cpw_10_min or 0.0,
                cpw_12_min=dto.cpw_12_min or 0.0,
                cpw_15_min=dto.cpw_15_min or 0.0,
                cpw_20_min=dto.cpw_20_min or 0.0,
                cpw_30_min=dto.cpw_30_min or 0.0,
                cpw_40_min=dto.cpw_40_min or 0.0,
            ),
        )
        return answer

    @staticmethod
    def from_dict_of_dataTransferObjects(dict_of_zwiftrider_powercurve_dto: Dict[str, ZwiftRiderCriticalPowerDataTransferObject]) -> Dict[str, "RiderCriticalPowerItem"]:
        answer = {
            key: RiderCriticalPowerItem.from_dataTransferObject(dto)
            for key, dto in dict_of_zwiftrider_powercurve_dto.items()
        }
        return answer

    
@dataclass
class RiderTeamItem:
    """
    """
    riders_working: list[ZwiftRiderItem] = field(default_factory=list)
    riders_resting: list[ZwiftRiderItem] = field(default_factory=list)

    @staticmethod
    def create(riders: list[ZwiftRiderItem]) -> "RiderTeamItem":
        riders.sort(key=lambda x: x.calculate_strength(), reverse=True)
        # assign rank to rank attr sarting with 1
        for i, rider in enumerate(riders):
            rider.rank = i + 1
        team = RiderTeamItem(riders_working=riders, riders_resting=[])
        return team

    def sort_riders() -> None:
        riders_working.sort(key=lambda x: x.calculate_strength(), reverse=True)
        riders_resting.sort(key=lambda x: x.calculate_strength(), reverse=True)

    def demote_rider_from_working_to_resting(rider: ZwiftRiderItem) -> None:
        riders_resting.append(rider)
        riders_working.remove(rider)
        sort_riders()

    def promote_rider_from_resting_to_working(self, rider: ZwiftRiderItem) -> None:
        riders_working.append(rider)
        riders_resting.remove(rider)
        sort_riders()



@dataclass(frozen=True, eq=True) 
class RiderWorkAssignmentItem:
    position: int = 1
    duration: float = 0
    speed: float = 0


@dataclass(frozen=True, eq=True) 
class RiderExertionItem:
    position: int = 0
    speed: float = 0
    duration: float = 0
    wattage: float = 0
    kilojoules: float = 0


@dataclass(frozen=True, eq=True)
class RiderAggregateEffortItem:
    total_duration: float = 0
    average_speed: float = 0
    total_distance: float = 0
    weighted_average_watts: float = 0
    normalized_average_watts: float = 0
    instantaneous_peak_wattage: float = 0
    position_at_peak_wattage: int = 0
    total_kilojoules_at_weighted_watts: float = 0
    total_kilojoules_at_normalized_watts: float = 0

@dataclass(frozen=True, eq=True) # immutable and hashable
class RiderStressItem():
    ftp: float = 0
    normalised_power: float = 0
    intensity_factor: float = 0

    peak_watts_divided_by_ftp_watts: float = 0
    position_at_peak_wattage : int = 0
    total_normalized_kilojoules_divided_by_ftp_kilojoules: float = 0

@dataclass(frozen=True, eq=True) # immutable and hashable
class RiderAnswerDisplayObject():
    name: str = ""
    zrs: float = 0
    zwiftftp_cat : str = ""
    velo_cat: int = 0
    cp_5_min_wkg: float = 0
    cp : float = 0
    ftp: float = 0
    ftp_wkg : float = 0
    p1_duration: float = 0
    p1_wkg: float = 0
    p1_div_ftp: float = 0
    p1_w: float = 0
    p2_w: float = 0
    p3_w: float = 0
    p4_w: float = 0
    ftp_intensity_factor: float = 0
    cp_intensity_factor: float = 0


def main():
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from tabulate import tabulate
    from typing import List, Union

    # # example: Instantiate ZwiftRiderItem using the example from Config 
    # # i.e.how we could do it from a JSON file
    example_data = ZwiftRiderItem.Config.json_schema_extra["johnh"]
    example_rider = ZwiftRiderDataTransferObject.model_validate(example_data)
    rider1 = ZwiftRiderItem.from_dataTransferObject(example_rider)

    # Log the instantiated object using a table
    rider_attrs = asdict(rider1)    
    logger.info("\nZwiftRider instantiated (ctor) from JSON config is:")
    logger.info("\n" + tabulate(rider_attrs.items(), tablefmt="plain"))

    # example : instantiate examples of two riders of differing ability. for each of them 
    # calculate wattage at a given speed (40kph)and in two positions in the peloton - 
    # position 1 and position 5. tabulate the results in a table and log it.
    example_data = ZwiftRiderItem.Config.json_schema_extra["markb"]
    example_rider = ZwiftRiderDataTransferObject.model_validate(example_data)
    rider2 = ZwiftRiderItem.from_dataTransferObject(example_rider)

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
    # at a given wattage (ftp=233) and tabulate neatly and log it.
    rider_john = ZwiftRiderItem(
        name=rider1.name, weight=rider1.weight, height=rider1.height, ftp=rider1.ftp, gender=rider1.gender, velo_rating=rider1.velo_rating)

    positions = range(1, 6)
    table: List[List[Union[str, float]]] = []
    headers = ["Position", f"Speed (km/h) at FTP {rider_john.ftp}"]

    for position in positions:
        # Calculate the speed for the given position and FTP
        speed = rider_john.calculate_speed_riding_in_the_peloton(rider_john.ftp, position)
        table.append([position, speed])

    # Log the table
    logger.info(f"\nSpeed for John H in positions 1 to 5 at FTP {rider_john.ftp}")
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))


if __name__ == "__main__":
    main()
