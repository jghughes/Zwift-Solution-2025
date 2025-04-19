from typing import Dict
from dataclasses import dataclass
from dataclasses import dataclass, field, asdict
from zwiftrider_dto import ZwiftRiderDTO 
from zwiftrider_criticalpower_dto import ZwiftRiderCriticalPowerDTO
from zwiftracing_dto import ZwiftRacingAppPostDTO
from zwiftpower_cp_graph_dto import ZwiftPowerCpGraphDTO
from jgh_formulae import estimate_speed_from_wattage, estimate_watts_from_speed, estimate_power_factor_in_peloton


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
    gender             : str = ""               # Gender of the rider
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
                "zwiftid": 1884456,
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
    def create(zwiftid: int, name: str, weight: float, height: float, gender: str, 
        ftp: float, zwift_racing_score: int, velo_rating: int
    ) -> 'ZwiftRiderItem':
        """
        Create a ZwiftRiderItem instance with the given parameters

        Args:
           zwiftid            (int)  : The Zwift ID of the rider.
            name               (str)  : The name of the rider.
            weight             (float): The weight of the rider in kilograms.
            height             (float): The height of the rider in centimeters.
            gender             (Gender): The gender of the rider.
            ftp                (float): Functional Threshold Power in watts.
            zwift_racing_score (int)  : Zwift racing score.
            velo_rating        (int)  : Velo rating.
    
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
    def to_dataTransferObject(item: "ZwiftRiderItem") -> ZwiftRiderDTO:
        """
        Convert a ZwiftRiderItem instance to a ZwiftRiderDTO.

        Args:
            item (ZwiftRiderItem): The ZwiftRiderItem instance to convert.

        Returns:
            ZwiftRiderDTO: The corresponding data transfer object.
        """
        return ZwiftRiderDTO(
            zwiftid=item.zwiftid,
            name=item.name,
            weight=item.weight,
            height=item.height,
            gender=item.gender,
            ftp=item.ftp,
            zwift_racing_score=item.zwift_racing_score,
            velo_rating=item.velo_rating
        )

    @staticmethod
    def from_dataTransferObject(dto: ZwiftRiderDTO) -> "ZwiftRiderItem":
        """
        Create a ZwiftRiderItem instance from a ZwiftRiderDTO.

        Args:
            dto (ZwiftRiderDTO): The data transfer object to convert.

        Returns:
            ZwiftRiderItem: The corresponding ZwiftRiderItem instance.
        """
        return ZwiftRiderItem(
            zwiftid=dto.zwiftid or 0,
            name=dto.name or "",
            weight=dto.weight or 0,
            height=dto.height or 0,
            gender=dto.gender or "",
            ftp=dto.ftp or 0,
            zwift_racing_score=dto.zwift_racing_score or 0,
            velo_rating=dto.velo_rating or 0
        )


@dataclass
class ZwiftRiderCriticalPowerItem:
    """
    A data class representing a Zwift rider's critical power data.
    The object can be converted to and from a data transfer object (DTO).

    Attributes:
        zwiftid   : int    The Zwift ID of the rider.
        name      : str    The name of the rider.
        cp_*      : float  Critical power values for various durations.
    """

    zwiftid: int = 0
    name: str = ""
    cp_1: float = 0.0
    cp_2: float = 0.0
    cp_3: float = 0.0
    cp_4: float = 0.0
    cp_5: float = 0.0
    cp_6: float = 0.0
    cp_7: float = 0.0
    cp_8: float = 0.0
    cp_9: float = 0.0
    cp_10: float = 0.0
    cp_11: float = 0.0
    cp_12: float = 0.0
    cp_13: float = 0.0
    cp_14: float = 0.0
    cp_15: float = 0.0
    cp_16: float = 0.0
    cp_17: float = 0.0
    cp_18: float = 0.0
    cp_19: float = 0.0
    cp_20: float = 0.0
    cp_21: float = 0.0
    cp_22: float = 0.0
    cp_23: float = 0.0
    cp_24: float = 0.0
    cp_25: float = 0.0
    cp_26: float = 0.0
    cp_27: float = 0.0
    cp_28: float = 0.0
    cp_29: float = 0.0
    cp_30: float = 0.0
    cp_35: float = 0.0
    cp_40: float = 0.0
    cp_45: float = 0.0
    cp_50: float = 0.0
    cp_55: float = 0.0
    cp_60: float = 0.0
    cp_70: float = 0.0
    cp_80: float = 0.0
    cp_90: float = 0.0
    cp_100: float = 0.0
    cp_110: float = 0.0
    cp_120: float = 0.0
    cp_150: float = 0.0
    cp_180: float = 0.0
    cp_210: float = 0.0
    cp_240: float = 0.0
    cp_270: float = 0.0
    cp_300: float = 0.0
    cp_330: float = 0.0
    cp_360: float = 0.0
    cp_390: float = 0.0
    cp_420: float = 0.0
    cp_450: float = 0.0
    cp_480: float = 0.0
    cp_510: float = 0.0
    cp_540: float = 0.0
    cp_570: float = 0.0
    cp_600: float = 0.0
    cp_660: float = 0.0
    cp_720: float = 0.0
    cp_780: float = 0.0
    cp_840: float = 0.0
    cp_900: float = 0.0
    cp_960: float = 0.0
    cp_1020: float = 0.0
    cp_1080: float = 0.0
    cp_1140: float = 0.0
    cp_1200: float = 0.0
    cp_1320: float = 0.0
    cp_1440: float = 0.0
    cp_1560: float = 0.0
    cp_1680: float = 0.0
    cp_1800: float = 0.0
    cp_1920: float = 0.0
    cp_2040: float = 0.0
    cp_2160: float = 0.0
    cp_2280: float = 0.0
    cp_2400: float = 0.0
    cp_2520: float = 0.0
    cp_2640: float = 0.0
    cp_2760: float = 0.0
    cp_2880: float = 0.0
    cp_3000: float = 0.0
    cp_3120: float = 0.0
    cp_3240: float = 0.0
    cp_3360: float = 0.0
    cp_3480: float = 0.0
    cp_3600: float = 0.0
    cp_3900: float = 0.0
    cp_4200: float = 0.0
    cp_4500: float = 0.0
    cp_4800: float = 0.0
    cp_5100: float = 0.0
    cp_5400: float = 0.0
    cp_5700: float = 0.0
    cp_6000: float = 0.0
    cp_6300: float = 0.0
    cp_6600: float = 0.0
    cp_7200: float = 0.0
    critical_power: float = 0.0
    anaerobic_work_capacity: float = 0.0
    inverse_coefficient: float = 0.0
    inverse_exponent: float = 0.0
    generated: str = ""
    model_applied: str = ""  # Alternatives are "inverse" for Inverse-Exponential model "cp" for Critical Power Model

    @classmethod
    def export_x_ordinates(cls) -> list[int]:
        """
        Returns a list of x ordinates for the critical power data.
        The x ordinates correspond to the time intervals for which
        critical power data is theoretically available.
        Returns:
            [int]: A list of x ordinates (time intervals in seconds).
        """
        answer: list[int] = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 
            21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 35, 40, 45, 50, 55, 60, 70, 80, 
            90, 100, 110, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 
            450, 480, 510, 540, 570, 600, 660, 720, 780, 840, 900, 960, 1020, 1080, 
            1140, 1200, 1320, 1440, 1560, 1680, 1800, 1920, 2040, 2160, 2280, 2400, 
            2520, 2640, 2760, 2880, 3000, 3120, 3240, 3360, 3480, 3600, 3900, 4200, 
            4500, 4800, 5100, 5400, 5700, 6000, 6300, 6600, 7200
        ]
        return answer;

    def export_cp_data(self) -> Dict[int, float]:
        """
        Map each attribute to a dictionary entry where the key is the number of seconds
        corresponding to the attribute name and the value is the attribute's value.

        Returns:
            Dict[int, float]: A dictionary mapping attribute names to (int, float) values.
        """
        answer = {
            1: self.cp_1,
            2: self.cp_2,
            3: self.cp_3,
            4: self.cp_4,
            5: self.cp_5,
            6: self.cp_6,
            7: self.cp_7,
            8: self.cp_8,
            9: self.cp_9,
            10: self.cp_10,
            11: self.cp_11,
            12: self.cp_12,
            13: self.cp_13,
            14: self.cp_14,
            15: self.cp_15,
            16: self.cp_16,
            17: self.cp_17,
            18: self.cp_18,
            19: self.cp_19,
            20: self.cp_20,
            21: self.cp_21,
            22: self.cp_22,
            23: self.cp_23,
            24: self.cp_24,
            25: self.cp_25,
            26: self.cp_26,
            27: self.cp_27,
            28: self.cp_28,
            29: self.cp_29,
            30: self.cp_30,
            35: self.cp_35,
            40: self.cp_40,
            45: self.cp_45,
            50: self.cp_50,
            55: self.cp_55,
            60: self.cp_60,
            70: self.cp_70,
            80: self.cp_80,
            90: self.cp_90,
            100: self.cp_100,
            110: self.cp_110,
            120: self.cp_120,
            150: self.cp_150,
            180: self.cp_180,
            210: self.cp_210,
            240: self.cp_240,
            270: self.cp_270,
            300: self.cp_300,
            330: self.cp_330,
            360: self.cp_360,
            390: self.cp_390,
            420: self.cp_420,
            450: self.cp_450,
            480: self.cp_480,
            510: self.cp_510,
            540: self.cp_540,
            570: self.cp_570,
            600: self.cp_600,
            660: self.cp_660,
            720: self.cp_720,
            780: self.cp_780,
            840: self.cp_840,
            900: self.cp_900,
            960: self.cp_960,
            1020: self.cp_1020,
            1080: self.cp_1080,
            1140: self.cp_1140,
            1200: self.cp_1200,
            1320: self.cp_1320,
            1440: self.cp_1440,
            1560: self.cp_1560,
            1680: self.cp_1680,
            1800: self.cp_1800,
            1920: self.cp_1920,
            2040: self.cp_2040,
            2160: self.cp_2160,
            2280: self.cp_2280,
            2400: self.cp_2400,
            2520: self.cp_2520,
            2640: self.cp_2640,
            2760: self.cp_2760,
            2880: self.cp_2880,
            3000: self.cp_3000,
            3120: self.cp_3120,
            3240: self.cp_3240,
            3360: self.cp_3360,
            3480: self.cp_3480,
            3600: self.cp_3600,
            3900: self.cp_3900,
            4200: self.cp_4200,
            4500: self.cp_4500,
            4800: self.cp_4800,
            5100: self.cp_5100,
            5400: self.cp_5400,
            5700: self.cp_5700,
            6000: self.cp_6000,
            6300: self.cp_6300,
            6600: self.cp_6600,
            7200: self.cp_7200,
        }

        # Filter out zero values (because they amount to invalid datapoints)
        answer = {k: v for k, v in answer.items() if v != 0}

        # Sort by key (if the dictionary is not empty)
        if answer:
            answer = dict(sorted(answer.items(), key=lambda item: item[0]))

        return answer

    def export_cp_data_for_best_fit_modelling(self) -> Dict[int, float]:
        """
        Map each attribute to a dictionary entry where the key is the number of seconds
        corresponding to the attribute name and the value is the attribute's value.

        Returns:
            Dict[int, float]: A dictionary mapping attribute names to (int, float) values.
        """
        answer = {
            1: self.cp_1,
            2: self.cp_2,
            3: self.cp_3,
            4: self.cp_4,
            5: self.cp_5,
            6: self.cp_6,
            7: self.cp_7,
            8: self.cp_8,
            9: self.cp_9,
            10: self.cp_10,
            11: self.cp_11,
            12: self.cp_12,
            13: self.cp_13,
            14: self.cp_14,
            15: self.cp_15,
            16: self.cp_16,
            17: self.cp_17,
            18: self.cp_18,
            19: self.cp_19,
            20: self.cp_20,
            21: self.cp_21,
            22: self.cp_22,
            23: self.cp_23,
            24: self.cp_24,
            25: self.cp_25,
            26: self.cp_26,
            27: self.cp_27,
            28: self.cp_28,
            29: self.cp_29,
            30: self.cp_30,
            35: self.cp_35,
            40: self.cp_40,
            45: self.cp_45,
            50: self.cp_50,
            55: self.cp_55,
            60: self.cp_60,
            70: self.cp_70,
            80: self.cp_80,
            90: self.cp_90,
            100: self.cp_100,
            110: self.cp_110,
            120: self.cp_120,
            150: self.cp_150,
            180: self.cp_180,
            210: self.cp_210,
            240: self.cp_240,
            270: self.cp_270,
            300: self.cp_300,
            330: self.cp_330,
            360: self.cp_360,
            390: self.cp_390,
            420: self.cp_420,
            450: self.cp_450,
            480: self.cp_480,
            510: self.cp_510,
            540: self.cp_540,
            570: self.cp_570,
            600: self.cp_600,
            660: self.cp_660,
            720: self.cp_720,
            780: self.cp_780,
            840: self.cp_840,
            900: self.cp_900,
            960: self.cp_960,
            1020: self.cp_1020,
            1080: self.cp_1080,
            1140: self.cp_1140,
            1200: self.cp_1200,
            1320: self.cp_1320,
            1440: self.cp_1440,
            1560: self.cp_1560,
            1680: self.cp_1680,
            1800: self.cp_1800,
            1920: self.cp_1920,
            2040: self.cp_2040,
            2160: self.cp_2160,
            2280: self.cp_2280,
            2400: self.cp_2400,
            2520: self.cp_2520,
            2640: self.cp_2640,
            2760: self.cp_2760,
            2880: self.cp_2880,
            3000: self.cp_3000,
            3120: self.cp_3120,
            3240: self.cp_3240,
            3360: self.cp_3360,
            3480: self.cp_3480,
            3600: self.cp_3600,
            3900: self.cp_3900,
            4200: self.cp_4200,
            4500: self.cp_4500,
            4800: self.cp_4800,
            5100: self.cp_5100,
            5400: self.cp_5400,
            5700: self.cp_5700,
            6000: self.cp_6000,
            6300: self.cp_6300,
            6600: self.cp_6600,
            7200: self.cp_7200,
        }

        # Filter out zero values (because they amount to invalid datapoints)
        answer = {k: v for k, v in answer.items() if v != 0}

        # Sort by key (if the dictionary is not empty)
        if answer:
            answer = dict(sorted(answer.items(), key=lambda item: item[0]))

        return answer


    def import_cp_data(self, input_data: Dict[int, float]) -> None:
        """
        Update the attributes of the instance based on the input_data dictionary.
        For each key in input_data, if the key corresponds to an attribute in self,
        update the attribute's value with the value from input_data.

        Args:
            input_data (Dict[int, float]): A dictionary where keys are durations (in seconds)
            and values are the corresponding critical power values.
        """
        mapping = {
            1: "cp_1",
            2: "cp_2",
            3: "cp_3",
            4: "cp_4",
            5: "cp_5",
            6: "cp_6",
            7: "cp_7",
            8: "cp_8",
            9: "cp_9",
            10: "cp_10",
            11: "cp_11",
            12: "cp_12",
            13: "cp_13",
            14: "cp_14",
            15: "cp_15",
            16: "cp_16",
            17: "cp_17",
            18: "cp_18",
            19: "cp_19",
            20: "cp_20",
            21: "cp_21",
            22: "cp_22",
            23: "cp_23",
            24: "cp_24",
            25: "cp_25",
            26: "cp_26",
            27: "cp_27",
            28: "cp_28",
            29: "cp_29",
            30: "cp_30",
            35: "cp_35",
            40: "cp_40",
            45: "cp_45",
            50: "cp_50",
            55: "cp_55",
            60: "cp_60",
            70: "cp_70",
            80: "cp_80",
            90: "cp_90",
            100: "cp_100",
            110: "cp_110",
            120: "cp_120",
            150: "cp_150",
            180: "cp_180",
            210: "cp_210",
            240: "cp_240",
            270: "cp_270",
            300: "cp_300",
            330: "cp_330",
            360: "cp_360",
            390: "cp_390",
            420: "cp_420",
            450: "cp_450",
            480: "cp_480",
            510: "cp_510",
            540: "cp_540",
            570: "cp_570",
            600: "cp_600",
            660: "cp_660",
            720: "cp_720",
            780: "cp_780",
            840: "cp_840",
            900: "cp_900",
            960: "cp_960",
            1020: "cp_1020",
            1080: "cp_1080",
            1140: "cp_1140",
            1200: "cp_1200",
            1320: "cp_1320",
            1440: "cp_1440",
            1560: "cp_1560",
            1680: "cp_1680",
            1800: "cp_1800",
            1920: "cp_1920",
            2040: "cp_2040",
            2160: "cp_2160",
            2280: "cp_2280",
            2400: "cp_2400",
            2520: "cp_2520",
            2640: "cp_2640",
            2760: "cp_2760",
            2880: "cp_2880",
            3000: "cp_3000",
            3120: "cp_3120",
            3240: "cp_3240",
            3360: "cp_3360",
            3480: "cp_3480",
            3600: "cp_3600",
            3900: "cp_3900",
            4200: "cp_4200",
            4500: "cp_4500",
            4800: "cp_4800",
            5100: "cp_5100",
            5400: "cp_5400",
            5700: "cp_5700",
            6000: "cp_6000",
            6300: "cp_6300",
            6600: "cp_6600",
            7200: "cp_7200",
        }

        for key, value in input_data.items():
            if key in mapping:
                setattr(self, mapping[key], value)

    @staticmethod
    def to_dataTransferObject(item: "ZwiftRiderCriticalPowerItem") -> ZwiftRiderCriticalPowerDTO:
        """
        Convert a ZwiftRiderCriticalPowerItem instance to a ZwiftRiderCriticalPowerDTO.

        Args:
            item (ZwiftRiderCriticalPowerItem): The ZwiftRiderCriticalPowerItem instance to convert.

        Returns:
            ZwiftRiderCriticalPowerDTO: The corresponding data transfer object.
        """
        return ZwiftRiderCriticalPowerDTO(
            zwiftid        = item.zwiftid,
            name           = item.name,
            cp_1           = item.cp_1,
            cp_2           = item.cp_2,
            cp_3           = item.cp_3,
            cp_4           = item.cp_4,
            cp_5           = item.cp_5,
            cp_6           = item.cp_6,
            cp_7           = item.cp_7,
            cp_8           = item.cp_8,
            cp_9           = item.cp_9,
            cp_10          = item.cp_10,
            cp_11          = item.cp_11,
            cp_13          = item.cp_13,
            cp_14          = item.cp_14,
            cp_15          = item.cp_15,
            cp_16          = item.cp_16,
            cp_17          = item.cp_17,
            cp_18          = item.cp_18,
            cp_19          = item.cp_19,
            cp_20          = item.cp_20,
            cp_21          = item.cp_21,
            cp_22          = item.cp_22,
            cp_23          = item.cp_23,
            cp_24          = item.cp_24,
            cp_25          = item.cp_25,
            cp_26          = item.cp_26,
            cp_27          = item.cp_27,
            cp_28          = item.cp_28,
            cp_29          = item.cp_29,
            cp_30          = item.cp_30,
            cp_35          = item.cp_35,
            cp_40          = item.cp_40,
            cp_45          = item.cp_45,
            cp_50          = item.cp_50,
            cp_55          = item.cp_55,
            cp_60          = item.cp_60,
            cp_70          = item.cp_70,
            cp_80          = item.cp_80,
            cp_90          = item.cp_90,
            cp_100         = item.cp_100,
            cp_110         = item.cp_110,
            cp_120         = item.cp_120,
            cp_150         = item.cp_150,
            cp_180         = item.cp_180,
            cp_210         = item.cp_210,
            cp_240         = item.cp_240,
            cp_270         = item.cp_270,
            cp_300         = item.cp_300,
            cp_330         = item.cp_330,
            cp_360         = item.cp_360,
            cp_390         = item.cp_390,
            cp_420         = item.cp_420,
            cp_450         = item.cp_450,
            cp_480         = item.cp_480,
            cp_510         = item.cp_510,
            cp_540         = item.cp_540,
            cp_570         = item.cp_570,
            cp_600         = item.cp_600,
            cp_660         = item.cp_660,
            cp_720         = item.cp_720,
            cp_780         = item.cp_780,
            cp_840         = item.cp_840,
            cp_900         = item.cp_900,
            cp_960         = item.cp_960,
            cp_1020        = item.cp_1020,
            cp_1080        = item.cp_1080,
            cp_1140        = item.cp_1140,
            cp_1200        = item.cp_1200,
            cp_1320        = item.cp_1320,
            cp_1440        = item.cp_1440,
            cp_1560        = item.cp_1560,
            cp_1680        = item.cp_1680,
            cp_1800        = item.cp_1800,
            cp_1920        = item.cp_1920,
            cp_2040        = item.cp_2040,
            cp_2160        = item.cp_2160,
            cp_2280        = item.cp_2280,
            cp_2400        = item.cp_2400,
            cp_2520        = item.cp_2520,
            cp_2640        = item.cp_2640,
            cp_2760        = item.cp_2760,
            cp_2880        = item.cp_2880,
            cp_3000        = item.cp_3000,
            cp_3120        = item.cp_3120,
            cp_3240        = item.cp_3240,
            cp_3360        = item.cp_3360,
            cp_3480        = item.cp_3480,
            cp_3600        = item.cp_3600,
            cp_3900        = item.cp_3900,
            cp_4200        = item.cp_4200,
            cp_4500        = item.cp_4500,
            cp_4800        = item.cp_4800,
            cp_5100        = item.cp_5100,
            cp_5400        = item.cp_5400,
            cp_5700        = item.cp_5700,
            cp_6000        = item.cp_6000,
            cp_6300        = item.cp_6300,
            cp_6600        = item.cp_6600,
            cp_7200        = item.cp_7200,
            critical_power             = item.critical_power,
            anaerobic_work_capacity            = item.anaerobic_work_capacity,
            inverse_coefficient  = item.inverse_coefficient,
            inverse_exponent    = item.inverse_exponent,
            generated      = item.generated,
            model_applied  = item.model_applied
        )

    @staticmethod
    def from_dataTransferObject(dto: ZwiftRiderCriticalPowerDTO) -> "ZwiftRiderCriticalPowerItem":
        """
        Create a ZwiftRiderCriticalPowerItem instance from a ZwiftRiderCriticalPowerDTO.

        Args:
            dto (ZwiftRiderCriticalPowerDTO): The data transfer object to convert.

        Returns:
            ZwiftRiderCriticalPowerItem: The corresponding ZwiftRiderCriticalPowerItem instance.
        """
        return ZwiftRiderCriticalPowerItem(
            zwiftid        = dto.zwiftid or 0,
            name           = dto.name or "",
            cp_1           = dto.cp_1 or 0.0,
            cp_2           = dto.cp_2 or 0.0,
            cp_3           = dto.cp_3 or 0.0,
            cp_4           = dto.cp_4 or 0.0,
            cp_5           = dto.cp_5 or 0.0,
            cp_6           = dto.cp_6 or 0.0,
            cp_7           = dto.cp_7 or 0.0,
            cp_8           = dto.cp_8 or 0.0,
            cp_9           = dto.cp_9 or 0.0,
            cp_10          = dto.cp_10 or 0.0,
            cp_11          = dto.cp_11 or 0.0,
            cp_13          = dto.cp_13 or 0.0,
            cp_14          = dto.cp_14 or 0.0,
            cp_15          = dto.cp_15 or 0.0,
            cp_16          = dto.cp_16 or 0.0,
            cp_17          = dto.cp_17 or 0.0,
            cp_18          = dto.cp_18 or 0.0,
            cp_19          = dto.cp_19 or 0.0,
            cp_20          = dto.cp_20 or 0.0,
            cp_21          = dto.cp_21 or 0.0,
            cp_22          = dto.cp_22 or 0.0,
            cp_23          = dto.cp_23 or 0.0,
            cp_24          = dto.cp_24 or 0.0,
            cp_25          = dto.cp_25 or 0.0,
            cp_26          = dto.cp_26 or 0.0,
            cp_27          = dto.cp_27 or 0.0,
            cp_28          = dto.cp_28 or 0.0,
            cp_29          = dto.cp_29 or 0.0,
            cp_30          = dto.cp_30 or 0.0,
            cp_35          = dto.cp_35 or 0.0,
            cp_40          = dto.cp_40 or 0.0,
            cp_45          = dto.cp_45 or 0.0,
            cp_50          = dto.cp_50 or 0.0,
            cp_55          = dto.cp_55 or 0.0,
            cp_60          = dto.cp_60 or 0.0,
            cp_70          = dto.cp_70 or 0.0,
            cp_80          = dto.cp_80 or 0.0,
            cp_90          = dto.cp_90 or 0.0,
            cp_100         = dto.cp_100 or 0.0,
            cp_110         = dto.cp_110 or 0.0,
            cp_120         = dto.cp_120 or 0.0,
            cp_150         = dto.cp_150 or 0.0,
            cp_180         = dto.cp_180 or 0.0,
            cp_210         = dto.cp_210 or 0.0,
            cp_240         = dto.cp_240 or 0.0,
            cp_270         = dto.cp_270 or 0.0,
            cp_300         = dto.cp_300 or 0.0,
            cp_330         = dto.cp_330 or 0.0,
            cp_360         = dto.cp_360 or 0.0,
            cp_390         = dto.cp_390 or 0.0,
            cp_420         = dto.cp_420 or 0.0,
            cp_450         = dto.cp_450 or 0.0,
            cp_480         = dto.cp_480 or 0.0,
            cp_510         = dto.cp_510 or 0.0,
            cp_540         = dto.cp_540 or 0.0,
            cp_570         = dto.cp_570 or 0.0,
            cp_600         = dto.cp_600 or 0.0,
            cp_660         = dto.cp_660 or 0.0,
            cp_720         = dto.cp_720 or 0.0,
            cp_780         = dto.cp_780 or 0.0,
            cp_840         = dto.cp_840 or 0.0,
            cp_900         = dto.cp_900 or 0.0,
            cp_960         = dto.cp_960 or 0.0,
            cp_1020        = dto.cp_1020 or 0.0,
            cp_1080        = dto.cp_1080 or 0.0,
            cp_1140        = dto.cp_1140 or 0.0,
            cp_1200        = dto.cp_1200 or 0.0,
            cp_1320        = dto.cp_1320 or 0.0,
            cp_1440        = dto.cp_1440 or 0.0,
            cp_1560        = dto.cp_1560 or 0.0,
            cp_1680        = dto.cp_1680 or 0.0,
            cp_1800        = dto.cp_1800 or 0.0,
            cp_1920        = dto.cp_1920 or 0.0,
            cp_2040        = dto.cp_2040 or 0.0,
            cp_2160        = dto.cp_2160 or 0.0,
            cp_2280        = dto.cp_2280 or 0.0,
            cp_2400        = dto.cp_2400 or 0.0,
            cp_2520        = dto.cp_2520 or 0.0,
            cp_2640        = dto.cp_2640 or 0.0,
            cp_2760        = dto.cp_2760 or 0.0,
            cp_2880        = dto.cp_2880 or 0.0,
            cp_3000        = dto.cp_3000 or 0.0,
            cp_3120        = dto.cp_3120 or 0.0,
            cp_3240        = dto.cp_3240 or 0.0,
            cp_3360        = dto.cp_3360 or 0.0,
            cp_3480        = dto.cp_3480 or 0.0,
            cp_3600        = dto.cp_3600 or 0.0,
            cp_3900        = dto.cp_3900 or 0.0,
            cp_4200        = dto.cp_4200 or 0.0,
            cp_4500        = dto.cp_4500 or 0.0,
            cp_4800        = dto.cp_4800 or 0.0,
            cp_5100        = dto.cp_5100 or 0.0,
            cp_5400        = dto.cp_5400 or 0.0,
            cp_5700        = dto.cp_5700 or 0.0,
            cp_6000        = dto.cp_6000 or 0.0,
            cp_6300        = dto.cp_6300 or 0.0,
            cp_6600        = dto.cp_6600 or 0.0,
            cp_7200        = dto.cp_7200 or 0.0,
            critical_power          = dto.critical_power or 0.0,
            anaerobic_work_capacity = dto.anaerobic_work_capacity or 0.0,
            inverse_coefficient     = dto.inverse_coefficient or 0.0,
            inverse_exponent        = dto.inverse_exponent or 0.0,
            generated               = dto.generated or "",
            model_applied           = dto.model_applied or ""  # Inverse Exponential model "inverse" or Critical Power Model "critical_power"
        )

    @staticmethod
    def from_zwift_racing_app_DTO(dto: ZwiftRacingAppPostDTO) -> "ZwiftRiderCriticalPowerItem":
        """
        Create a ZwiftRiderCriticalPowerItem instance from a ZwiftRacingAppPostDTO.
        The ZwiftRacingApp seemingly stores just the CP values for 5, 15, 30, 60, 120, 300 and 1200 seconds.
        Not sure how it derives these values, and not sure if it does or doesn't use them to derive 
        critical power and other derivatives 

        Args:
            dto (ZwiftRacingAppPostDTO): The data transfer object to convert.

        Returns:
            ZwiftRiderCriticalPowerItem: The corresponding ZwiftRiderCriticalPowerItem instance.
        """
        return ZwiftRiderCriticalPowerItem(
            zwiftid   = int(dto.riderId) if dto.riderId else 0,
            name      = dto.name or "",
            cp_5      = dto.power.w5 if dto.power and dto.power.w5 else 0.0,
            cp_15     = dto.power.w15 if dto.power and dto.power.w15 else 0.0,
            cp_30     = dto.power.w30 if dto.power and dto.power.w30 else 0.0,
            cp_60     = dto.power.w60 if dto.power and dto.power.w60 else 0.0,
            cp_120    = dto.power.w120 if dto.power and dto.power.w120 else 0.0,
            cp_300    = dto.power.w300 if dto.power and dto.power.w300 else 0.0,
            cp_1200   = dto.power.w1200 if dto.power and dto.power.w1200 else 0.0,
            critical_power          = dto.power.CP if dto.power and dto.power.CP else 0.0,
            anaerobic_work_capacity = dto.power.AWC if dto.power and dto.power.AWC else 0.0
        )

    @staticmethod
    def from_zwiftpower_cp_graph_DTO(dto: ZwiftPowerCpGraphDTO) -> "ZwiftRiderCriticalPowerItem":
        """
        Create a ZwiftRiderCriticalPowerItem instance from a ZwiftPowerCpGraphDTO.

        Args:
            dto (ZwiftPowerCpGraphDTO): The data transfer object to convert.

        Returns:
            ZwiftRiderCriticalPowerItem: The corresponding ZwiftRiderCriticalPowerItem instance.
        """
        # Extract efforts from the "90days" key, if available
        efforts_90days = dto.efforts.get("90days", []) if dto.efforts else []

        # Map efforts to a dictionary of time (x) to power (y)
        cp_data = {effort.x: float(effort.y) for effort in efforts_90days if effort.x and effort.y}

        # Create an instance of ZwiftRiderCriticalPowerItem
        critical_power_item = ZwiftRiderCriticalPowerItem()

        critical_power_item.import_cp_data(cp_data)

        return critical_power_item


# @dataclass(frozen=True, eq=True) 
# class RiderTeamItem:
#     """
#     """
#     riders_working: list[ZwiftRiderItem] = field(default_factory=list)
#     riders_resting: list[ZwiftRiderItem] = field(default_factory=list)

#     @staticmethod
#     def create(riders: list[ZwiftRiderItem]) -> "RiderTeamItem":
#         riders.sort(key=lambda x: x.calculate_strength(), reverse=True)
#         # assign rank to rank attr sarting with 1
#         for i, rider in enumerate(riders):
#             rider.rank = i + 1
#         team = RiderTeamItem(riders_working=riders, riders_resting=[])
#         return team

#     def sort_riders(self) -> None:
#         riders_working.sort(key=lambda x: x.calculate_strength(), reverse=True)
#         riders_resting.sort(key=lambda x: x.calculate_strength(), reverse=True)

#     def demote_rider_from_working_to_resting(self, rider: ZwiftRiderItem) -> None:
#         riders_resting.append(rider)
#         riders_working.remove(rider)
#         sort_riders()

#     def promote_rider_from_resting_to_working(self, rider: ZwiftRiderItem) -> None:
#         riders_working.append(rider)
#         riders_resting.remove(rider)
#         sort_riders()


@dataclass(frozen=True, eq=True) 
class RiderWorkAssignmentItem:
    position: int = 1
    duration: float = 0
    speed: float = 0


@dataclass(frozen=True, eq=True) 
class RiderExertionItem:
    current_location_in_paceline: int = 0
    speed_kph: float = 0
    duration: float = 0
    wattage: float = 0
    kilojoules: float = 0


@dataclass
class RiderAnswerItem():
    critical_power                    : float = 0
    anaerobic_work_capacity               : float = 0
    speed_kph             : float = 0
    pull_duration         : float = 0
    pull_wkg              : float = 0
    pull_w_over_ftp       : float = 0
    p1_w                  : float = 0
    p2_w                  : float = 0
    p3_w                  : float = 0
    p4_w                  : float = 0
    p__w                  : float = 0
    ftp_intensity_factor  : float = 0
    cp_intensity_factor   : float = 0

    
@dataclass
class RiderAnswerDisplayObject():
    name                  : str   = ""
    pretty_cat_descriptor : str   = ""
    zrs_score             : float = 0
    zrs_cat               : str   = ""
    zwiftftp_cat          : str   = ""
    velo_cat              : str   = ""
    zwift_cp              : float = 0
    zwift_w_prime         : float = 0
    ftp                   : float = 0
    ftp_wkg               : float = 0
    speed_kph             : float = 0
    pull_duration         : float = 0
    pull_wkg              : float = 0
    pull_w_over_ftp       : str   = ""
    p1_4                  : str   = ""
    ftp_intensity_factor  : float = 0
    cp_intensity_factor   : float = 0

    
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
    example_rider = ZwiftRiderDTO.model_validate(example_data)
    rider1 = ZwiftRiderItem.from_dataTransferObject(example_rider)

    # Log the instantiated object using a table
    rider_attrs = asdict(rider1)    
    logger.info("\nZwiftRider instantiated (ctor) from JSON config is:")
    logger.info("\n" + tabulate(rider_attrs.items(), tablefmt="plain"))

    # example : instantiate examples of two riders of differing ability. for each of them 
    # calculate wattage at a given speed (40kph)and in two positions in the peloton - 
    # position 1 and position 5. tabulate the results in a table and log it.
    example_data = ZwiftRiderItem.Config.json_schema_extra["markb"]
    example_rider = ZwiftRiderDTO.model_validate(example_data)
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
