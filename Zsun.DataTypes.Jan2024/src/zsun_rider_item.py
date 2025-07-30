from dataclasses import dataclass,  asdict
from typing import Optional
import numpy as np
from jgh_number import safe_divide
from zsun_rider_dto import ZsunDTO 
from jgh_power_curve_fit_models import decay_model_numpy

@dataclass(frozen=True, eq=True)  # immutable and hashable, we use this as a dictionary key everywhere
class ZsunItem:
    """
    A frozen data class representing a Zwift rider.
    Can be used as a cache key or dictionary key, or in a set.
    """

    zwift_id                          : str   = ""    # Zwift ID of the rider
    name                              : str   = ""    # Name of the rider
    weight_kg                         : float = 0.0   # Weight of the rider in kilograms
    height_cm                         : float = 0.0   # Height of the rider in centimeters
    gender                            : str   = ""    # Gender of the rider
    age_years                         : float = 0.0   # Age of the rider in years
    age_group                          : str   = ""    # Age group of the rider
    zwift_ftp                         : float = 0.0   # Originates in Zwift profile
    zwiftpower_zFTP                   : float = 0.0   # Originates in Zwiftpower profile
    zwiftracingapp_zpFTP              : float = 0.0   # Originates in Zwiftracingapp profile
    zsun_one_hour_watts               : float = 0.0   # Calculated by JGH
    zsun_CP                           : float = 0.0   # Critical power in watts
    zsun_AWC                          : float = 0.0   # Critical power W' in kilojoules
    zwift_zrs                         : float = 0.0   # Zwift racing score
    zwift_cat                         : str   = ""    # A+, A, B, C, D, E
    zwiftracingapp_score              : float = 0.0   # Velo score typically over 1000
    zwiftracingapp_cat_num            : int   = 0     # Velo rating 1 to 10
    zwiftracingapp_cat_name           : str   = ""    # Copper, Silver, Gold etc
    zwiftracingapp_CP                 : float = 0.0   # Critical power in watts
    zwiftracingapp_AWC                : float = 0.0   # Anaerobic work capacity in kilojoules
    zsun_one_hour_curve_coefficient   : float = 0.0   # Coefficient for FTP modeling
    zsun_one_hour_curve_exponent      : float = 0.0   # Exponent for FTP modeling
    zsun_TTT_pull_curve_coefficient   : float = 0.0   # Coefficient for pull modeling
    zsun_TTT_pull_curve_exponent      : float = 0.0   # Exponent for pull modeling
    zsun_TTT_pull_curve_fit_r_squared : float = 0.0   # R-squared value for the curve fit of the FTP data
    zsun_when_curves_fitted           : str   = ""    # Timestamp indicating when the models were fitted

    class Config:
        # Define the extra JSON schema for the class in the form of a dictionary of riders
        json_schema_extra = {
            "davek": {
                "zwift_id": "3147366",
                "name": "Dave Konicek",
                "weight_kg": 73.4,
                "height_cm": 182,
                "gender": "m",
                "age_years": 37.0,
                "age_group": "Mas",
                "zwift_ftp": 289,
                "zwiftpower_zFTP": 253,
                "zwiftracingapp_zpFTP": 276,
                "zsun_one_hour_watts": 265,
                "zsun_CP": 481,
                "zsun_AWC": 5.7,
                "zwift_zrs": 766,
                "zwift_cat": "B",
                "zwiftracingapp_score": 1961,
                "zwiftracingapp_cat_num": 2,
                "zwiftracingapp_cat_name": "Ruby",
                "zwiftracingapp_CP": 267,
                "zwiftracingapp_AWC": 44,
                "zsun_one_hour_curve_coefficient": 664.0079147534638,
                "zsun_one_hour_curve_exponent": 0.11239298363950606,
                "zsun_TTT_pull_curve_coefficient": 1745.6066111916828,
                "zsun_TTT_pull_curve_exponent": 0.26940852871547233,
                "zsun_TTT_pull_curve_fit_r_squared": 0.99,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.465243"
            },
            "huskyc": {
                "zwift_id": "5134",
                "name": "Husky Crone",
                "weight_kg": 75.5,
                "height_cm": 178,
                "gender": "m",
                "age_years": 35.0,
                "age_group": "Mas",
                "zwift_ftp": 289,
                "zwiftpower_zFTP": 0,
                "zwiftracingapp_zpFTP": 269,
                "zsun_one_hour_watts": 262,
                "zsun_CP": 435,
                "zsun_AWC": 6.0,
                "zwift_zrs": 559,
                "zwift_cat": "B",
                "zwiftracingapp_score": 1558,
                "zwiftracingapp_cat_num": 4,
                "zwiftracingapp_cat_name": "Sapphire",
                "zwiftracingapp_CP": 274,
                "zwiftracingapp_AWC": 20,
                "zsun_one_hour_curve_coefficient": 520.4954289732605,
                "zsun_one_hour_curve_exponent": 0.08389032975096743,
                "zsun_TTT_pull_curve_coefficient": 955.1603211890762,
                "zsun_TTT_pull_curve_exponent": 0.18357620329753058,
                "zsun_TTT_pull_curve_fit_r_squared": 0.96,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.535358"
            },
            "scottm": {
                "zwift_id": "11526",
                "name": "Scott McVeigh",
                "weight_kg": 78.0,
                "height_cm": 165,
                "gender": "m",
                "age_years": 55.0,
                "age_group": "50+",
                "zwift_ftp": 266,
                "zwiftpower_zFTP": 266,
                "zwiftracingapp_zpFTP": 248,
                "zsun_one_hour_watts": 237,
                "zsun_CP": 407,
                "zsun_AWC": 5.5,
                "zwift_zrs": 509,
                "zwift_cat": "B",
                "zwiftracingapp_score": 1537,
                "zwiftracingapp_cat_num": 4,
                "zwiftracingapp_cat_name": "Sapphire",
                "zwiftracingapp_CP": 240,
                "zwiftracingapp_AWC": 29,
                "zsun_one_hour_curve_coefficient": 506.95534041277796,
                "zsun_one_hour_curve_exponent": 0.0928305762893673,
                "zsun_TTT_pull_curve_coefficient": 818.2572203302822,
                "zsun_TTT_pull_curve_exponent": 0.16785965369458963,
                "zsun_TTT_pull_curve_fit_r_squared": 0.95,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.605522"
            },
            "johnh": {
                "zwift_id": "1884456",
                "name": "John Hughes",
                "weight_kg": 75.4,
                "height_cm": 174,
                "gender": "m",
                "age_years": 68.0,
                "age_group": "60+",
                "zwift_ftp": 255,
                "zwiftpower_zFTP": 0,
                "zwiftracingapp_zpFTP": 240,
                "zsun_one_hour_watts": 235,
                "zsun_CP": 321,
                "zsun_AWC": 2.0,
                "zwift_zrs": 354,
                "zwift_cat": "C",
                "zwiftracingapp_score": 1068,
                "zwiftracingapp_cat_num": 7,
                "zwiftracingapp_cat_name": "Gold",
                "zwiftracingapp_CP": 235,
                "zwiftracingapp_AWC": 27,
                "zsun_one_hour_curve_coefficient": 438.41811711142964,
                "zsun_one_hour_curve_exponent": 0.07613242272294136,
                "zsun_TTT_pull_curve_coefficient": 368.9228335727515,
                "zsun_TTT_pull_curve_exponent": 0.041421410263352096,
                "zsun_TTT_pull_curve_fit_r_squared": 0.69,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.590622"
            },
            "joshn": {
                "zwift_id": "2508033",
                "name": "Josh N",
                "weight_kg": 101.0,
                "height_cm": 178,
                "gender": "m",
                "age_years": 48.0,
                "age_group": "Vet",
                "zwift_ftp": 283,
                "zwiftpower_zFTP": 0,
                "zwiftracingapp_zpFTP": 259,
                "zsun_one_hour_watts": 247,
                "zsun_CP": 420,
                "zsun_AWC": 6.3,
                "zwift_zrs": 0,
                "zwift_cat": "",
                "zwiftracingapp_score": 966,
                "zwiftracingapp_cat_num": 8,
                "zwiftracingapp_cat_name": "Silver",
                "zwiftracingapp_CP": 261,
                "zwiftracingapp_AWC": 22,
                "zsun_one_hour_curve_coefficient": 635.6351183277075,
                "zsun_one_hour_curve_exponent": 0.11525850433801628,
                "zsun_TTT_pull_curve_coefficient": 954.4693803074022,
                "zsun_TTT_pull_curve_exponent": 0.18875993101642763,
                "zsun_TTT_pull_curve_fit_r_squared": 0.96,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.547244"
            },
            "brent": {
                "zwift_id": "480698",
                "name": "Brent",
                "weight_kg": 75.1,
                "height_cm": 180,
                "gender": "m",
                "age_years": 64.0,
                "age_group": "60+",
                "zwift_ftp": 248,
                "zwiftpower_zFTP": 0,
                "zwiftracingapp_zpFTP": 252,
                "zsun_one_hour_watts": 233,
                "zsun_CP": 387,
                "zsun_AWC": 5.9,
                "zwift_zrs": 0,
                "zwift_cat": "",
                "zwiftracingapp_score": 1134,
                "zwiftracingapp_cat_num": 7,
                "zwiftracingapp_cat_name": "Gold",
                "zwiftracingapp_CP": 244,
                "zwiftracingapp_AWC": 16,
                "zsun_one_hour_curve_coefficient": 490.839505002798,
                "zsun_one_hour_curve_exponent": 0.09124723263727438,
                "zsun_TTT_pull_curve_coefficient": 754.0586848474131,
                "zsun_TTT_pull_curve_exponent": 0.16464100889054065,
                "zsun_TTT_pull_curve_fit_r_squared": 0.98,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.528257"
            },
            "coryc": {
                "zwift_id": "5569057",
                "name": "Cory Cook",
                "weight_kg": 90.7,
                "height_cm": 186,
                "gender": "m",
                "age_years": 58.0,
                "age_group": "50+",
                "zwift_ftp": 290,
                "zwiftpower_zFTP": 0,
                "zwiftracingapp_zpFTP": 271,
                "zsun_one_hour_watts": 264,
                "zsun_CP": 457,
                "zsun_AWC": 7.3,
                "zwift_zrs": 436,
                "zwift_cat": "C",
                "zwiftracingapp_score": 1266,
                "zwiftracingapp_cat_num": 6,
                "zwiftracingapp_cat_name": "Platinum",
                "zwiftracingapp_CP": 275,
                "zwiftracingapp_AWC": 32,
                "zsun_one_hour_curve_coefficient": 648.1030002578349,
                "zsun_one_hour_curve_exponent": 0.10975216676298859,
                "zsun_TTT_pull_curve_coefficient": 925.1077031333853,
                "zsun_TTT_pull_curve_exponent": 0.1654803344602741,
                "zsun_TTT_pull_curve_fit_r_squared": 0.86,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.563525"
            },
            "richardm": {
                "zwift_id": "1193",
                "name": "Richard Mann",
                "weight_kg": 93.0,
                "height_cm": 178,
                "gender": "m",
                "age_years": 59.0,
                "age_group": "50+",
                "zwift_ftp": 220,
                "zwiftpower_zFTP": 0,
                "zwiftracingapp_zpFTP": 203,
                "zsun_one_hour_watts": 196,
                "zsun_CP": 269,
                "zsun_AWC": 6.6,
                "zwift_zrs": 187,
                "zwift_cat": "D",
                "zwiftracingapp_score": 645,
                "zwiftracingapp_cat_num": 10,
                "zwiftracingapp_cat_name": "Copper",
                "zwiftracingapp_CP": 196,
                "zwiftracingapp_AWC": 22,
                "zsun_one_hour_curve_coefficient": 393.721985511704,
                "zsun_one_hour_curve_exponent": 0.08546639813143812,
                "zsun_TTT_pull_curve_coefficient": 617.2705888756522,
                "zsun_TTT_pull_curve_exponent": 0.1590388131288181,
                "zsun_TTT_pull_curve_fit_r_squared": 0.95,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.459256"
            },
            "timr": {
                "zwift_id": "5421258",
                "name": "Tim Reid",
                "weight_kg": 79.8,
                "height_cm": 185,
                "gender": "m",
                "age_years": 42.0,
                "age_group": "Vet",
                "zwift_ftp": 366,
                "zwiftpower_zFTP": 0,
                "zwiftracingapp_zpFTP": 380,
                "zsun_one_hour_watts": 346,
                "zsun_CP": 515,
                "zsun_AWC": 6.3,
                "zwift_zrs": 705,
                "zwift_cat": "A",
                "zwiftracingapp_score": 2186,
                "zwiftracingapp_cat_num": 2,
                "zwiftracingapp_cat_name": "Ruby",
                "zwiftracingapp_CP": 384,
                "zwiftracingapp_AWC": 17,
                "zsun_one_hour_curve_coefficient": 835.4522228502348,
                "zsun_one_hour_curve_exponent": 0.10750304608455272,
                "zsun_TTT_pull_curve_coefficient": 1066.8447652505567,
                "zsun_TTT_pull_curve_exponent": 0.15556453497632458,
                "zsun_TTT_pull_curve_fit_r_squared": 0.98,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.514248"
            },
            "meridithl": {
                "zwift_id": "1707548",
                "name": "Meridith Leubner",
                "weight_kg": 59.0,
                "height_cm": 158,
                "gender": "f",
                "age_years": 49.0,
                "age_group": "Vet",
                "zwift_ftp": 236,
                "zwiftpower_zFTP": 224,
                "zwiftracingapp_zpFTP": 220,
                "zsun_one_hour_watts": 214,
                "zsun_CP": 320,
                "zsun_AWC": 3.4,
                "zwift_zrs": 398,
                "zwift_cat": "B",
                "zwiftracingapp_score": 1310,
                "zwiftracingapp_cat_num": 5,
                "zwiftracingapp_cat_name": "Amethyst",
                "zwiftracingapp_CP": 219,
                "zwiftracingapp_AWC": 18,
                "zsun_one_hour_curve_coefficient": 387.17415636798984,
                "zsun_one_hour_curve_exponent": 0.07228861452587262,
                "zsun_TTT_pull_curve_coefficient": 522.5841631649076,
                "zsun_TTT_pull_curve_exponent": 0.11649441181261071,
                "zsun_TTT_pull_curve_fit_r_squared": 0.96,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.479252"
            },
            "melissaw": {
                "zwift_id": "1657744",
                "name": "Melissa Warwick N",
                "weight_kg": 59.0,
                "height_cm": 175,
                "gender": "f",
                "age_years": 48.0,
                "age_group": "Vet",
                "zwift_ftp": 218,
                "zwiftpower_zFTP": 0,
                "zwiftracingapp_zpFTP": 213,
                "zsun_one_hour_watts": 206,
                "zsun_CP": 268,
                "zsun_AWC": 5.7,
                "zwift_zrs": 354,
                "zwift_cat": "B",
                "zwiftracingapp_score": 1088,
                "zwiftracingapp_cat_num": 7,
                "zwiftracingapp_cat_name": "Gold",
                "zwiftracingapp_CP": 203,
                "zwiftracingapp_AWC": 18,
                "zsun_one_hour_curve_coefficient": 329.38967469903315,
                "zsun_one_hour_curve_exponent": 0.05759325401657411,
                "zsun_TTT_pull_curve_coefficient": 519.6131258856989,
                "zsun_TTT_pull_curve_exponent": 0.13271100392618762,
                "zsun_TTT_pull_curve_fit_r_squared": 0.98,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.573522"
            },
            "davide": {
                "zwift_id": "4945836",
                "name": "David Evanetich",
                "weight_kg": 89.4,
                "height_cm": 175,
                "gender": "m",
                "age_years": 60.0,
                "age_group": "60+",
                "zwift_ftp": 244,
                "zwiftpower_zFTP": 243,
                "zwiftracingapp_zpFTP": 250,
                "zsun_one_hour_watts": 232,
                "zsun_CP": 330,
                "zsun_AWC": 5.2,
                "zwift_zrs": 268,
                "zwift_cat": "C",
                "zwiftracingapp_score": 871,
                "zwiftracingapp_cat_num": 8,
                "zwiftracingapp_cat_name": "Silver",
                "zwiftracingapp_CP": 253,
                "zwiftracingapp_AWC": 10,
                "zsun_one_hour_curve_coefficient": 461.94246292014464,
                "zsun_one_hour_curve_exponent": 0.08405525316957085,
                "zsun_TTT_pull_curve_coefficient": 942.5213896273015,
                "zsun_TTT_pull_curve_exponent": 0.21045384587938612,
                "zsun_TTT_pull_curve_fit_r_squared": 0.94,
                "zsun_when_curves_fitted": "2025-05-08T15:32:40.579625"
            },
        }

    @staticmethod
    def create(zwiftid: str, name: str, weight_kg: float, height_cm: float, gender: str, 
        zwiftpower_zFTP: float, zwift_zrs: int, zwiftracingapp_cat_num: int
    ) -> 'ZsunItem':
        """
        Create a ZsunItem instance with the given parameters

        Args:
           zwift_id            (int)  : The Zwift ID of the rider.
            name               (str)  : The name of the rider.
            weight_kg             (float): The weight_kg of the rider in kilograms.
            height_cm             (float): The height_cm of the rider in centimeters.
            gender             (Gender): The gender of the rider.
            zwiftpower_zFTP                (float): Functional Threshold Power in watts.
            zwift_zrs (int)  : Zwift racing score.
            zwiftracingapp_cat_num        (int)  : Velo rating.
    
        Returns:
            ZsunItem: A ZsunItem instance with the given parameters.
        """

        instance = ZsunItem(
            zwift_id=zwiftid,
            name=name,
            weight_kg=weight_kg,
            height_cm=height_cm,
            gender=gender,
            zwiftpower_zFTP=zwiftpower_zFTP,
            zwift_zrs=zwift_zrs,
            zwiftracingapp_cat_num=zwiftracingapp_cat_num
        )

        return instance

    def get_strength_wkg(self) -> float:
        if self.weight_kg == 0:
            return safe_divide(self.get_standard_1_minute_pull_watts(),80.0) # arbitrary default 80kg
        return safe_divide(self.get_standard_1_minute_pull_watts(),self.weight_kg)

    def get_standard_pull_watts(self, seconds : float)-> float:

        permissable_watts = self.get_one_hour_watts() # default

        if seconds == 0:
            permissable_watts = self.get_standard_30sec_pull_watts()
        if seconds == 30:
            permissable_watts = self.get_standard_30sec_pull_watts()
        if seconds == 60:
            permissable_watts = self.get_standard_1_minute_pull_watts()
        if seconds == 120:
            permissable_watts = self.get_standard_2_minute_pull_watts()
        if seconds == 180:
            permissable_watts = self.get_standard_3_minute_pull_watts()
        if seconds == 240:
            permissable_watts = self.get_standard_4_minute_pull_watts()
         
        return permissable_watts

    def get_standard_00sec_pull_watts(self) -> float:
        return self.get_standard_30sec_pull_watts()

    def get_standard_30sec_pull_watts(self) -> float:
        # apply 3.5 minute watts
        pull_short = decay_model_numpy(np.array([210]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([210]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = max(pull_short[0], one_hour[0])
        return answer

    def get_standard_1_minute_pull_watts(self) -> float:
        # apply 5 minute watts
        pull_medium = decay_model_numpy(np.array([300]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([300]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = max(pull_medium[0], one_hour[0])
        return answer

    def get_standard_2_minute_pull_watts(self) -> float:
        # # apply 12 minute watts
        pull_long = decay_model_numpy(np.array([720]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([720]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = max(pull_long[0], one_hour[0])
        return answer

    def get_standard_3_minute_pull_watts(self) -> float:
        # apply 15 minute watts
        pull_long = decay_model_numpy(np.array([900]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([900]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = max(pull_long[0], one_hour[0])
        return answer

    def get_standard_4_minute_pull_watts(self) -> float:
        # apply 18 minute watts
        one_hour = decay_model_numpy(np.array([1080]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = one_hour[0]
        return answer

    def get_standard_5_minute_pull_watts(self) -> float:
        # apply 20 minute watts
        one_hour = decay_model_numpy(np.array([1200]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = one_hour[0]
        return answer

    def get_one_hour_watts(self) -> float:

        ftp = decay_model_numpy(np.array([3_600]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)

        answer =  ftp[0]

        return answer

    def get_one_hour_wkg(self) -> float:
        if self.weight_kg == 0:
            return 0.0
        return safe_divide( self.get_one_hour_watts(), self.weight_kg)

    def get_watts_per_kg(self, wattage : float) -> float:
        if self.weight_kg == 0:
            return 0.0
        return safe_divide(wattage,self.weight_kg)

    def get_n_second_watts(self, seconds: float) -> float:

        one_hour_curve = decay_model_numpy(np.array([seconds]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)

        if seconds < 900:
            pull_curve = decay_model_numpy(np.array([seconds]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
            answer = max(pull_curve[0], one_hour_curve[0])

        elif seconds >= 900 and seconds < 1200:
            pull_curve = decay_model_numpy(np.array([seconds]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
            # Linear transition from max(...) at 900s to one_hour_curve[0] at 1200s
            t = (seconds - 900) / 300.0
            start_val = max(pull_curve[0], one_hour_curve[0])
            end_val = one_hour_curve[0]
            answer = (1 - t) * start_val + t * end_val
        else: 
            answer = one_hour_curve[0]

        return answer

    def get_critical_power_watts(self) -> float:
        return self.zsun_CP

    def get_anaerobic_work_capacity_kj(self) -> float:
        return safe_divide(self.zsun_AWC,1_000.0)

    def get_zwiftracingapp_zpFTP_wkg(self) -> float:
        if self.weight_kg == 0:
            return 0.0
        return safe_divide(self.zwiftracingapp_zpFTP, self.weight_kg)

    def get_when_models_fitted(self) -> str:
        return self.zsun_when_curves_fitted

    @staticmethod
    def to_dataTransferObject(item: Optional["ZsunItem"]) -> ZsunDTO:
        if item is None:
            return ZsunDTO()
        return ZsunDTO(
            zwift_id                          = item.zwift_id,
            name                              = item.name,
            weight_kg                         = item.weight_kg,
            height_cm                         = item.height_cm,
            gender                            = item.gender,
            age_years                         = item.age_years,
            age_group                          = item.age_group,
            zwift_ftp                         = item.zwift_ftp,
            zwiftpower_zFTP                   = item.zwiftpower_zFTP,
            zwiftracingapp_zpFTP              = item.zwiftracingapp_zpFTP,
            zsun_one_hour_watts               = item.get_one_hour_watts(),
            zsun_CP                           = item.zsun_CP,
            zsun_AWC                          = item.zsun_AWC,
            zwift_zrs                         = item.zwift_zrs,
            zwift_cat                         = item.zwift_cat,
            zwiftracingapp_score              = item.zwiftracingapp_score,
            zwiftracingapp_cat_num            = item.zwiftracingapp_cat_num,
            zwiftracingapp_cat_name           = item.zwiftracingapp_cat_name,
            zwiftracingapp_CP                 = item.zwiftracingapp_CP,
            zwiftracingapp_AWC                = item.zwiftracingapp_AWC,
            zsun_one_hour_curve_coefficient   = item.zsun_one_hour_curve_coefficient,
            zsun_one_hour_curve_exponent      = item.zsun_one_hour_curve_exponent,
            zsun_TTT_pull_curve_coefficient   = item.zsun_TTT_pull_curve_coefficient,
            zsun_TTT_pull_curve_exponent      = item.zsun_TTT_pull_curve_exponent,
            zsun_TTT_pull_curve_fit_r_squared = item.zsun_TTT_pull_curve_fit_r_squared,
            zsun_when_curves_fitted           = item.zsun_when_curves_fitted,
        )

    @staticmethod
    def from_dataTransferObject(dto: Optional[ZsunDTO]) -> "ZsunItem":
        if dto is None:
            return ZsunItem()
        return ZsunItem(
            zwift_id                          = dto.zwift_id or "",
            name                              = dto.name or "",
            weight_kg                         = dto.weight_kg or 0.0,
            height_cm                         = dto.height_cm or 0.0,
            gender                            = dto.gender or "",
            age_years                         = dto.age_years or 0.0,
            age_group                          = dto.age_group or "",
            zwift_ftp                         = dto.zwift_ftp or 0.0,
            zwiftpower_zFTP                   = dto.zwiftpower_zFTP or 0.0,
            zwiftracingapp_zpFTP              = dto.zwiftracingapp_zpFTP or 0.0,
            zsun_one_hour_watts               = dto.zsun_one_hour_watts or 0.0,
            zsun_CP                           = dto.zsun_CP or 0.0,
            zsun_AWC                          = dto.zsun_AWC or 0.0,
            zwift_zrs                         = dto.zwift_zrs or 0.0,
            zwift_cat                         = dto.zwift_cat or "",
            zwiftracingapp_score              = dto.zwiftracingapp_score or 0.0,
            zwiftracingapp_cat_num            = dto.zwiftracingapp_cat_num or 0,
            zwiftracingapp_cat_name           = dto.zwiftracingapp_cat_name or "",
            zwiftracingapp_CP                 = dto.zwiftracingapp_CP or 0.0,
            zwiftracingapp_AWC                = dto.zwiftracingapp_AWC or 0.0,
            zsun_one_hour_curve_coefficient   = dto.zsun_one_hour_curve_coefficient or 0.0,
            zsun_one_hour_curve_exponent      = dto.zsun_one_hour_curve_exponent or 0.0,
            zsun_TTT_pull_curve_coefficient   = dto.zsun_TTT_pull_curve_coefficient or 0.0,
            zsun_TTT_pull_curve_exponent      = dto.zsun_TTT_pull_curve_exponent or 0.0,
            zsun_TTT_pull_curve_fit_r_squared = dto.zsun_TTT_pull_curve_fit_r_squared or 0.0,
            zsun_when_curves_fitted           = dto.zsun_when_curves_fitted or "",
        )


def main():

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from tabulate import tabulate
    from typing import List, Union

    # # example: Instantiate ZsunItem using the example from Config 
    # # i.e.how we could do it from a JSON file
    example_data = ZsunItem.Config.json_schema_extra["johnh"]
    example_rider = ZsunDTO.model_validate(example_data)
    rider1 = ZsunItem.from_dataTransferObject(example_rider)

    # Log the instantiated object using a table
    rider_attrs = asdict(rider1)    
    logger.info("\nZwiftRider instantiated (ctor) from JSON config is:")
    logger.info("\n" + tabulate(rider_attrs.items(), tablefmt="plain"))

if __name__ == "__main__":
    main()
