from typing import Dict, Optional
from dataclasses import dataclass

from zsun_watts_properties_dto import ZsunWattsPropertiesDTO
from zwiftpower_watts_ordinates_dto import ZwiftPowerWattsOrdinatesDTO, EffortDTO
from zwiftracingapp_rider_particulars_dto import ZwiftRacingAppRiderParticularsDTO


@dataclass
class EffortItem:
    x    : int = 0      # X-coordinate (must be int for dict key)
    y    : float = 0.0  # Y-coordinate
    date : int   = 0    # Date as a Unix timestamp
    zid  : str   = ""   # Zwift ID

    @staticmethod
    def from_dataTransferObject(dto: Optional[EffortDTO]) -> "EffortItem":
        if dto is None:
            return EffortItem()
        return EffortItem(
            x    = dto.x or 0,
            y    = float(dto.y or 0),  # Cast y to float
            date = dto.date or 0,
            zid  = dto.zid or "",
    )

    @staticmethod
    def to_dataTransferObject(item: Optional["EffortItem"]) -> EffortDTO:
        if item is None:
            return EffortDTO()
        return EffortDTO(
            x    = item.x,
            y    = int(item.y),  # Cast y back to int
            date = item.date,
            zid  = item.zid,
    )

@dataclass
class ZsunWattsPropertiesItem:
    """
    A data class representing a Zwift rider's 90-day best power data obtained from ZwiftfPower.
    The object can be converted to and from a data transfer object (DTO).

    Attributes:
        zwift_id   : int    The Zwift ID of the rider.
        name      : str    The name of the rider.
        cp_*      : float  Critical power values for various durations.
    """

    zwift_id   : str   = ""
    bp_1      : float = 0.0
    bp_2      : float = 0.0
    bp_3      : float = 0.0
    bp_4      : float = 0.0
    bp_5      : float = 0.0
    bp_6      : float = 0.0
    bp_7      : float = 0.0
    bp_8      : float = 0.0
    bp_9      : float = 0.0
    bp_10     : float = 0.0
    bp_11     : float = 0.0
    bp_12     : float = 0.0
    bp_13     : float = 0.0
    bp_14     : float = 0.0
    bp_15     : float = 0.0
    bp_16     : float = 0.0
    bp_17     : float = 0.0
    bp_18     : float = 0.0
    bp_19     : float = 0.0
    bp_20     : float = 0.0
    bp_21     : float = 0.0
    bp_22     : float = 0.0
    bp_23     : float = 0.0
    bp_24     : float = 0.0
    bp_25     : float = 0.0
    bp_26     : float = 0.0
    bp_27     : float = 0.0
    bp_28     : float = 0.0
    bp_29     : float = 0.0
    bp_30     : float = 0.0
    bp_35     : float = 0.0
    bp_40     : float = 0.0
    bp_45     : float = 0.0
    bp_50     : float = 0.0
    bp_55     : float = 0.0
    bp_60     : float = 0.0
    bp_70     : float = 0.0
    bp_80     : float = 0.0
    bp_90     : float = 0.0
    bp_100    : float = 0.0
    bp_110    : float = 0.0
    bp_120    : float = 0.0
    bp_150    : float = 0.0
    bp_180    : float = 0.0
    bp_210    : float = 0.0
    bp_240    : float = 0.0
    bp_270    : float = 0.0
    bp_300    : float = 0.0
    bp_330    : float = 0.0
    bp_360    : float = 0.0
    bp_390    : float = 0.0
    bp_420    : float = 0.0
    bp_450    : float = 0.0
    bp_480    : float = 0.0
    bp_510    : float = 0.0
    bp_540    : float = 0.0
    bp_570    : float = 0.0
    bp_600    : float = 0.0
    bp_660    : float = 0.0
    bp_720    : float = 0.0
    bp_780    : float = 0.0
    bp_840    : float = 0.0
    bp_900    : float = 0.0
    bp_960    : float = 0.0
    bp_1020   : float = 0.0
    bp_1080   : float = 0.0
    bp_1140   : float = 0.0
    bp_1200   : float = 0.0
    bp_1320   : float = 0.0
    bp_1440   : float = 0.0
    bp_1560   : float = 0.0
    bp_1680   : float = 0.0
    bp_1800   : float = 0.0
    bp_1920   : float = 0.0
    bp_2040   : float = 0.0
    bp_2160   : float = 0.0
    bp_2280   : float = 0.0
    bp_2400   : float = 0.0
    bp_2520   : float = 0.0
    bp_2640   : float = 0.0
    bp_2760   : float = 0.0
    bp_2880   : float = 0.0
    bp_3000   : float = 0.0
    bp_3120   : float = 0.0
    bp_3240   : float = 0.0
    bp_3360   : float = 0.0
    bp_3480   : float = 0.0
    bp_3600   : float = 0.0
    bp_3900   : float = 0.0
    bp_4200   : float = 0.0
    bp_4500   : float = 0.0
    bp_4800   : float = 0.0
    bp_5100   : float = 0.0
    bp_5400   : float = 0.0
    bp_5700   : float = 0.0
    bp_6000   : float = 0.0
    bp_6300   : float = 0.0
    bp_6600   : float = 0.0
    bp_7200   : float = 0.0

    @classmethod
    def export_all_x_ordinates(cls) -> list[int]:
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


    def export_all_x_y_ordinates(self) -> Dict[int, float]:
        """
        Map each attribute to a dictionary entry where the key is the number of seconds
        corresponding to the attribute name and the value is the attribute's value.

        Returns:
            Dict[int, float]: A dictionary mapping attribute names to (int, float) values.
        """
        answer = {
            1: self.bp_1,
            2: self.bp_2,
            3: self.bp_3,
            4: self.bp_4,
            5: self.bp_5,
            6: self.bp_6,
            7: self.bp_7,
            8: self.bp_8,
            9: self.bp_9,
            10: self.bp_10,
            11: self.bp_11,
            12: self.bp_12,
            13: self.bp_13,
            14: self.bp_14,
            15: self.bp_15,
            16: self.bp_16,
            17: self.bp_17,
            18: self.bp_18,
            19: self.bp_19,
            20: self.bp_20,
            21: self.bp_21,
            22: self.bp_22,
            23: self.bp_23,
            24: self.bp_24,
            25: self.bp_25,
            26: self.bp_26,
            27: self.bp_27,
            28: self.bp_28,
            29: self.bp_29,
            30: self.bp_30,
            35: self.bp_35,
            40: self.bp_40,
            45: self.bp_45,
            50: self.bp_50,
            55: self.bp_55,
            60: self.bp_60,
            70: self.bp_70,
            80: self.bp_80,
            90: self.bp_90,
            100: self.bp_100,
            110: self.bp_110,
            120: self.bp_120,
            150: self.bp_150,
            180: self.bp_180,
            210: self.bp_210,
            240: self.bp_240,
            270: self.bp_270,
            300: self.bp_300,
            330: self.bp_330,
            360: self.bp_360,
            390: self.bp_390,
            420: self.bp_420,
            450: self.bp_450,
            480: self.bp_480,
            510: self.bp_510,
            540: self.bp_540,
            570: self.bp_570,
            600: self.bp_600,
            660: self.bp_660,
            720: self.bp_720,
            780: self.bp_780,
            840: self.bp_840,
            900: self.bp_900,
            960: self.bp_960,
            1020: self.bp_1020,
            1080: self.bp_1080,
            1140: self.bp_1140,
            1200: self.bp_1200,
            1320: self.bp_1320,
            1440: self.bp_1440,
            1560: self.bp_1560,
            1680: self.bp_1680,
            1800: self.bp_1800,
            1920: self.bp_1920,
            2040: self.bp_2040,
            2160: self.bp_2160,
            2280: self.bp_2280,
            2400: self.bp_2400,
            2520: self.bp_2520,
            2640: self.bp_2640,
            2760: self.bp_2760,
            2880: self.bp_2880,
            3000: self.bp_3000,
            3120: self.bp_3120,
            3240: self.bp_3240,
            3360: self.bp_3360,
            3480: self.bp_3480,
            3600: self.bp_3600,
            3900: self.bp_3900,
            4200: self.bp_4200,
            4500: self.bp_4500,
            4800: self.bp_4800,
            5100: self.bp_5100,
            5400: self.bp_5400,
            5700: self.bp_5700,
            6000: self.bp_6000,
            6300: self.bp_6300,
            6600: self.bp_6600,
            7200: self.bp_7200,
        }

        # Filter out zero values (because they amount to invalid datapoints)
        answer = {k: v for k, v in answer.items() if v != 0}

        # Sort by key (if the dictionary is not empty)
        if answer:
            answer = dict(sorted(answer.items(), key=lambda item: item[0]))

        return answer


    def export_x_y_ordinates_for_cp_w_prime_modelling(self) -> Dict[int, float]:
        """
        Zwift doesn't explicitly use CP, although they do have zMap which generally
        appears to be around P_5 minutes. zMap is used as a criterion for race categories.
        The standard test for CP in sports science is a 3 minute test to collapse.
        Map each attribute to a dictionary entry where the key is the number of seconds
        corresponding to the attribute name and the value is the attribute's value.

        Returns:
            Dict[int, float]: A dictionary mapping attribute names to (int, float) values.
        """

        answer = {
            # 1: self.bp_1,
            # 2: self.bp_2,
            # 3: self.bp_3,
            # 4: self.bp_4, #old limit
            # 5: self.bp_5,
            # 6: self.bp_6,
            # 7: self.bp_7,
            # 8: self.bp_8,
            # 9: self.bp_9,
            10: self.bp_10,
            11: self.bp_11,
            12: self.bp_12,
            13: self.bp_13,
            14: self.bp_14, # new limit
            15: self.bp_15,
            16: self.bp_16,
            17: self.bp_17,
            18: self.bp_18,
            19: self.bp_19,
            20: self.bp_20,
            21: self.bp_21,
            22: self.bp_22,
            23: self.bp_23,
            24: self.bp_24,
            25: self.bp_25,
            26: self.bp_26,
            27: self.bp_27,
            28: self.bp_28,
            29: self.bp_29,
            30: self.bp_30,
            35: self.bp_35,
            40: self.bp_40,
            45: self.bp_45,
            50: self.bp_50,
            55: self.bp_55,
            60: self.bp_60,
            70: self.bp_70,
            80: self.bp_80,
            90: self.bp_90,
            100: self.bp_100,
            110: self.bp_110,
            120: self.bp_120,
            150: self.bp_150,
            180: self.bp_180,# new new new limit
            # 210: self.bp_210,
            # 240: self.bp_240,
            # 270: self.bp_270,
            # 300: self.bp_300, # new new limit
            # 330: self.bp_330,
            # 360: self.bp_360,
            # 390: self.bp_390,
            # 420: self.bp_420,
            # 450: self.bp_450,
            # 480: self.bp_480,
            # 510: self.bp_510,
            # 540: self.bp_540,
            # 570: self.bp_570,
            # 600: self.bp_600,
            # 660: self.bp_660, # new limit
            # 720: self.bp_720,
            # 780: self.bp_780,
            # 840: self.bp_840,
            # 900: self.bp_900,
            # 960: self.bp_960,
            # 1020: self.bp_1020,
            # 1080: self.bp_1080,
            # 1140: self.bp_1140,# previous limit
            # 1200: self.bp_1200,
            # 1320: self.bp_1320,
            # 1440: self.bp_1440,
            # 1560: self.bp_1560,
            # 1680: self.bp_1680,
            # 1800: self.bp_1800,
            # 1920: self.bp_1920,
            # 2040: self.bp_2040,
            # 2160: self.bp_2160,
            # 2280: self.bp_2280,
            # 2400: self.bp_2400,
            # 2520: self.bp_2520,
            # 2640: self.bp_2640,
            # 2760: self.bp_2760,
            # 2880: self.bp_2880,
            # 3000: self.bp_3000,
            # 3120: self.bp_3120,
            # 3240: self.bp_3240,
            # 3360: self.bp_3360,
            # 3480: self.bp_3480,
            # 3600: self.bp_3600,
            # 3900: self.bp_3900,
            # 4200: self.bp_4200,
            # 4500: self.bp_4500,
            # 4800: self.bp_4800,
            # 5100: self.bp_5100,
            # 5400: self.bp_5400,
            # 5700: self.bp_5700,
            # 6000: self.bp_6000,
            # 6300: self.bp_6300,
            # 6600: self.bp_6600,
            # 7200: self.bp_7200,
        }

        # Filter out zero values (because they amount to invalid datapoints)
        answer = {k: v for k, v in answer.items() if v != 0}

        # Sort by key (if the dictionary is not empty)
        if answer:
            answer = dict(sorted(answer.items(), key=lambda item: item[0]))

        return answer


    def export_x_y_ordinates_for_pull_zone_modelling(self) -> Dict[int, float]:
        """
        Is this case we will do a model to individually determine the 
        peak limit for pulling. The TTT calculator uses 1.3x FTP.  
        On most people's 90_day best curves from ZwiftPower, a notch is clearly visible 
        where some sort of peak stability exists in the 5-10 minute range. This might or 
        might not bear some resemblance to Zwifts' zMap 

        Dated : Easter Monday, April 21st 2025

        Map each datapoint to a dictionary entry where the key is the number of seconds
        corresponding to the attribute name and the value is the attribute's value.

        Returns:
            Dict[int, float]: A dictionary mapping attribute names to (int, float) values.
        """

        answer = {
            # 1: self.bp_1,
            # 2: self.bp_2,
            # 3: self.bp_3,
            # 4: self.bp_4,
            # 5: self.bp_5,
            # 6: self.bp_6,
            # 7: self.bp_7,
            # 8: self.bp_8,
            # 9: self.bp_9,
            # 10: self.bp_10,
            # 11: self.bp_11,
            # 12: self.bp_12,
            # 13: self.bp_13,
            # 14: self.bp_14,
            # # 15: self.bp_15,
            # 16: self.bp_16,
            # 17: self.bp_17,
            # 18: self.bp_18,
            # 19: self.bp_19,
            # 20: self.bp_20,
            # 21: self.bp_21,
            # 22: self.bp_22,
            # 23: self.bp_23,
            # 24: self.bp_24,
            # 25: self.bp_25,
            # 26: self.bp_26,
            # 27: self.bp_27,
            # 28: self.bp_28,
            # 29: self.bp_29,
            # 30: self.bp_30,
            # 35: self.bp_35,
            # 40: self.bp_40,
            # 45: self.bp_45,
            # 50: self.bp_50,
            # 55: self.bp_55,
            # 60: self.bp_60,
            # 70: self.bp_70,
            # 80: self.bp_80,
            # 90: self.bp_90,
            # 100: self.bp_100,
            # 110: self.bp_110, # old limit
            120: self.bp_120,
            150: self.bp_150, #new limit
            180: self.bp_180,
            210: self.bp_210,
            240: self.bp_240,
            270: self.bp_270,
            300: self.bp_300,
            330: self.bp_330,
            360: self.bp_360,
            390: self.bp_390,
            420: self.bp_420,
            # 450: self.bp_450,#new new limit
            # 480: self.bp_480,
            # 510: self.bp_510,
            # 540: self.bp_540,
            # 570: self.bp_570,
            # 600: self.bp_600, #new new limit 
            # 660: self.bp_660,
            # 720: self.bp_720,
            # 780: self.bp_780,
            # 840: self.bp_840,
            # 900: self.bp_900,
            # 960: self.bp_960, #new limit
            # 1020: self.bp_1020,
            # 1080: self.bp_1080,
            # 1140: self.bp_1140,
            # 1200: self.bp_1200,
            # 1320: self.bp_1320, # old limit
            # 1440: self.bp_1440,
            # 1560: self.bp_1560,
            # 1680: self.bp_1680,
            # 1800: self.bp_1800,
            # 1920: self.bp_1920,
            # 2040: self.bp_2040,
            # 2160: self.bp_2160,
            # 2280: self.bp_2280,
            # 2400: self.bp_2400,
            # 2520: self.bp_2520,
            # 2640: self.bp_2640,
            # 2760: self.bp_2760,
            # 2880: self.bp_2880,
            # 3000: self.bp_3000,
            # 3120: self.bp_3120,
            # 3240: self.bp_3240,
            # 3360: self.bp_3360,
            # 3480: self.bp_3480,
            # 3600: self.bp_3600,
            # 3900: self.bp_3900,
            # 4200: self.bp_4200,
            # 4500: self.bp_4500,
            # 4800: self.bp_4800,
            # 5100: self.bp_5100,
            # 5400: self.bp_5400,
            # 5700: self.bp_5700,
            # 6000: self.bp_6000,
            # 6300: self.bp_6300,
            # 6600: self.bp_6600,
            # 7200: self.bp_7200,
        }

        # Filter out zero values (because they amount to invalid datapoints)
        answer = {k: v for k, v in answer.items() if v != 0}

        # Sort by key (if the dictionary is not empty)
        if answer:
            answer = dict(sorted(answer.items(), key=lambda item: item[0]))

        return answer


    def export_x_y_ordinates_for_one_hour_zone_modelling(self) -> Dict[int, float]:
        """

        Zwift doesn't use FTP per se. They use black magic to come up with zFTP.
        zFTP is normally somewhere between P_30 minutes and P_40 minutes. 
        zFTP is used as a criterion for race categories.In this case we will
        do a more accurate model to individually determine what FTP is meant to be,
        namely true Functional Threshold Power for P_60 minutes. 

        Dated : Easter Monday, April 21st 2025

        Map each datapoint to a dictionary entry where the key is the number of seconds
        corresponding to the attribute name and the value is the attribute's value.

        Returns:
            Dict[int, float]: A dictionary mapping attribute names to (int, float) values.
        """

        answer = {
            # 1: self.bp_1,
            # 2: self.bp_2,
            # 3: self.bp_3,
            # 4: self.bp_4,
            # 5: self.bp_5,
            # 6: self.bp_6,
            # 7: self.bp_7,
            # 8: self.bp_8,
            # 9: self.bp_9,
            # 10: self.bp_10,
            # 11: self.bp_11,
            # 12: self.bp_12,
            # 13: self.bp_13,
            # 14: self.bp_14,
            # # 15: self.bp_15,
            # 16: self.bp_16,
            # 17: self.bp_17,
            # 18: self.bp_18,
            # 19: self.bp_19,
            # 20: self.bp_20,
            # 21: self.bp_21,
            # 22: self.bp_22,
            # 23: self.bp_23,
            # 24: self.bp_24,
            # 25: self.bp_25,
            # 26: self.bp_26,
            # 27: self.bp_27,
            # 28: self.bp_28,
            # 29: self.bp_29,
            # 30: self.bp_30,
            # 35: self.bp_35,
            # 40: self.bp_40,
            # 45: self.bp_45,
            # 50: self.bp_50,
            # 55: self.bp_55,
            # 60: self.bp_60,
            # 70: self.bp_70,
            # 80: self.bp_80,
            # 90: self.bp_90,
            # 100: self.bp_100,
            # 110: self.bp_110,
            # 120: self.bp_120,
            # 150: self.bp_150,
            # 180: self.bp_180,
            # 210: self.bp_210,
            # 240: self.bp_240,
            # 270: self.bp_270,
            # 300: self.bp_300,
            # 330: self.bp_330,
            # 360: self.bp_360,
            # 390: self.bp_390,
            # 420: self.bp_420, # new cut off here
            450: self.bp_450,
            480: self.bp_480,
            510: self.bp_510,
            540: self.bp_540, 
            570: self.bp_570,# previous cut off here
            600: self.bp_600,
            660: self.bp_660,
            720: self.bp_720,
            780: self.bp_780,
            840: self.bp_840,
            900: self.bp_900,
            960: self.bp_960,
            1020: self.bp_1020,
            1080: self.bp_1080,
            1140: self.bp_1140,
            1200: self.bp_1200,
            1320: self.bp_1320,
            1440: self.bp_1440,
            1560: self.bp_1560,
            1680: self.bp_1680,
            1800: self.bp_1800,
            1920: self.bp_1920,
            2040: self.bp_2040,
            2160: self.bp_2160,
            2280: self.bp_2280,
            2400: self.bp_2400, # previously here
            # 2520: self.bp_2520,
            # 2640: self.bp_2640,
            # 2760: self.bp_2760,
            # 2880: self.bp_2880,
            # 3000: self.bp_3000,
            # 3120: self.bp_3120,
            # 3240: self.bp_3240,
            # 3360: self.bp_3360,
            # 3480: self.bp_3480,
            # 3600: self.bp_3600,
            # 3900: self.bp_3900,
            # 4200: self.bp_4200,
            # 4500: self.bp_4500,
            # 4800: self.bp_4800,
            # 5100: self.bp_5100,
            # 5400: self.bp_5400,
            # 5700: self.bp_5700,
            # 6000: self.bp_6000,
            # 6300: self.bp_6300,
            # 6600: self.bp_6600,
            # 7200: self.bp_7200,
        }

        # Filter out zero values (because they amount to invalid datapoints)
        answer = {k: v for k, v in answer.items() if v != 0}

        # Sort by key (if the dictionary is not empty)
        if answer:
            answer = dict(sorted(answer.items(), key=lambda item: item[0]))

        return answer


    def import_x_y_ordinates(self, input_data: Dict[int, float]) -> None:
        """
        Update the attributes of the instance based on the input_data dictionary.
        For each key in input_data, if the key corresponds to an attribute in self,
        update the attribute's value with the value from input_data.

        Args:
            input_data (Dict[int, float]): A dictionary where keys are durations (in seconds)
            and values are the corresponding critical power values.
        """
        mapping = {
            1: "bp_1",
            2: "bp_2",
            3: "bp_3",
            4: "bp_4",
            5: "bp_5",
            6: "bp_6",
            7: "bp_7",
            8: "bp_8",
            9: "bp_9",
            10: "bp_10",
            11: "bp_11",
            12: "bp_12",
            13: "bp_13",
            14: "bp_14",
            15: "bp_15",
            16: "bp_16",
            17: "bp_17",
            18: "bp_18",
            19: "bp_19",
            20: "bp_20",
            21: "bp_21",
            22: "bp_22",
            23: "bp_23",
            24: "bp_24",
            25: "bp_25",
            26: "bp_26",
            27: "bp_27",
            28: "bp_28",
            29: "bp_29",
            30: "bp_30",
            35: "bp_35",
            40: "bp_40",
            45: "bp_45",
            50: "bp_50",
            55: "bp_55",
            60: "bp_60",
            70: "bp_70",
            80: "bp_80",
            90: "bp_90",
            100: "bp_100",
            110: "bp_110",
            120: "bp_120",
            150: "bp_150",
            180: "bp_180",
            210: "bp_210",
            240: "bp_240",
            270: "bp_270",
            300: "bp_300",
            330: "bp_330",
            360: "bp_360",
            390: "bp_390",
            420: "bp_420",
            450: "bp_450",
            480: "bp_480",
            510: "bp_510",
            540: "bp_540",
            570: "bp_570",
            600: "bp_600",
            660: "bp_660",
            720: "bp_720",
            780: "bp_780",
            840: "bp_840",
            900: "bp_900",
            960: "bp_960",
            1020: "bp_1020",
            1080: "bp_1080",
            1140: "bp_1140",
            1200: "bp_1200",
            1320: "bp_1320",
            1440: "bp_1440",
            1560: "bp_1560",
            1680: "bp_1680",
            1800: "bp_1800",
            1920: "bp_1920",
            2040: "bp_2040",
            2160: "bp_2160",
            2280: "bp_2280",
            2400: "bp_2400",
            2520: "bp_2520",
            2640: "bp_2640",
            2760: "bp_2760",
            2880: "bp_2880",
            3000: "bp_3000",
            3120: "bp_3120",
            3240: "bp_3240",
            3360: "bp_3360",
            3480: "bp_3480",
            3600: "bp_3600",
            3900: "bp_3900",
            4200: "bp_4200",
            4500: "bp_4500",
            4800: "bp_4800",
            5100: "bp_5100",
            5400: "bp_5400",
            5700: "bp_5700",
            6000: "bp_6000",
            6300: "bp_6300",
            6600: "bp_6600",
            7200: "bp_7200",
        }

        for key, value in input_data.items():
            if key in mapping:
                setattr(self, mapping[key], value)


    @staticmethod
    def to_dataTransferObject(item: "ZsunWattsPropertiesItem") -> ZsunWattsPropertiesDTO:
        return ZsunWattsPropertiesDTO(
            zwift_id        = item.zwift_id,
            bp_1           = item.bp_1,
            bp_2           = item.bp_2,
            bp_3           = item.bp_3,
            bp_4           = item.bp_4,
            bp_5           = item.bp_5,
            bp_6           = item.bp_6,
            bp_7           = item.bp_7,
            bp_8           = item.bp_8,
            bp_9           = item.bp_9,
            bp_10          = item.bp_10,
            bp_11          = item.bp_11,
            bp_12          = item.bp_12,
            bp_13          = item.bp_13,
            bp_14          = item.bp_14,
            bp_15          = item.bp_15,
            bp_16          = item.bp_16,
            bp_17          = item.bp_17,
            bp_18          = item.bp_18,
            bp_19          = item.bp_19,
            bp_20          = item.bp_20,
            bp_21          = item.bp_21,
            bp_22          = item.bp_22,
            bp_23          = item.bp_23,
            bp_24          = item.bp_24,
            bp_25          = item.bp_25,
            bp_26          = item.bp_26,
            bp_27          = item.bp_27,
            bp_28          = item.bp_28,
            bp_29          = item.bp_29,
            bp_30          = item.bp_30,
            bp_35          = item.bp_35,
            bp_40          = item.bp_40,
            bp_45          = item.bp_45,
            bp_50          = item.bp_50,
            bp_55          = item.bp_55,
            bp_60          = item.bp_60,
            bp_70          = item.bp_70,
            bp_80          = item.bp_80,
            bp_90          = item.bp_90,
            bp_100         = item.bp_100,
            bp_110         = item.bp_110,
            bp_120         = item.bp_120,
            bp_150         = item.bp_150,
            bp_180         = item.bp_180,
            bp_210         = item.bp_210,
            bp_240         = item.bp_240,
            bp_270         = item.bp_270,
            bp_300         = item.bp_300,
            bp_330         = item.bp_330,
            bp_360         = item.bp_360,
            bp_390         = item.bp_390,
            bp_420         = item.bp_420,
            bp_450         = item.bp_450,
            bp_480         = item.bp_480,
            bp_510         = item.bp_510,
            bp_540         = item.bp_540,
            bp_570         = item.bp_570,
            bp_600         = item.bp_600,
            bp_660         = item.bp_660,
            bp_720         = item.bp_720,
            bp_780         = item.bp_780,
            bp_840         = item.bp_840,
            bp_900         = item.bp_900,
            bp_960         = item.bp_960,
            bp_1020        = item.bp_1020,
            bp_1080        = item.bp_1080,
            bp_1140        = item.bp_1140,
            bp_1200        = item.bp_1200,
            bp_1320        = item.bp_1320,
            bp_1440        = item.bp_1440,
            bp_1560        = item.bp_1560,
            bp_1680        = item.bp_1680,
            bp_1800        = item.bp_1800,
            bp_1920        = item.bp_1920,
            bp_2040        = item.bp_2040,
            bp_2160        = item.bp_2160,
            bp_2280        = item.bp_2280,
            bp_2400        = item.bp_2400,
            bp_2520        = item.bp_2520,
            bp_2640        = item.bp_2640,
            bp_2760        = item.bp_2760,
            bp_2880        = item.bp_2880,
            bp_3000        = item.bp_3000,
            bp_3120        = item.bp_3120,
            bp_3240        = item.bp_3240,
            bp_3360        = item.bp_3360,
            bp_3480        = item.bp_3480,
            bp_3600        = item.bp_3600,
            bp_3900        = item.bp_3900,
            bp_4200        = item.bp_4200,
            bp_4500        = item.bp_4500,
            bp_4800        = item.bp_4800,
            bp_5100        = item.bp_5100,
            bp_5400        = item.bp_5400,
            bp_5700        = item.bp_5700,
            bp_6000        = item.bp_6000,
            bp_6300        = item.bp_6300,
            bp_6600        = item.bp_6600,
            bp_7200        = item.bp_7200,
            )


    @staticmethod
    def from_dataTransferObject(dto: Optional[ZsunWattsPropertiesDTO]) -> "ZsunWattsPropertiesItem":
        if dto is None:
            return ZsunWattsPropertiesItem()
        return ZsunWattsPropertiesItem(
            zwift_id        = dto.zwift_id or "",
            bp_1           = dto.bp_1 or 0.0,
            bp_2           = dto.bp_2 or 0.0,
            bp_3           = dto.bp_3 or 0.0,
            bp_4           = dto.bp_4 or 0.0,
            bp_5           = dto.bp_5 or 0.0,
            bp_6           = dto.bp_6 or 0.0,
            bp_7           = dto.bp_7 or 0.0,
            bp_8           = dto.bp_8 or 0.0,
            bp_9           = dto.bp_9 or 0.0,
            bp_10          = dto.bp_10 or 0.0,
            bp_11          = dto.bp_11 or 0.0,
            bp_12          = dto.bp_12 or 0.0,
            bp_13          = dto.bp_13 or 0.0,
            bp_14          = dto.bp_14 or 0.0,
            bp_15          = dto.bp_15 or 0.0,
            bp_16          = dto.bp_16 or 0.0,
            bp_17          = dto.bp_17 or 0.0,
            bp_18          = dto.bp_18 or 0.0,
            bp_19          = dto.bp_19 or 0.0,
            bp_20          = dto.bp_20 or 0.0,
            bp_21          = dto.bp_21 or 0.0,
            bp_22          = dto.bp_22 or 0.0,
            bp_23          = dto.bp_23 or 0.0,
            bp_24          = dto.bp_24 or 0.0,
            bp_25          = dto.bp_25 or 0.0,
            bp_26          = dto.bp_26 or 0.0,
            bp_27          = dto.bp_27 or 0.0,
            bp_28          = dto.bp_28 or 0.0,
            bp_29          = dto.bp_29 or 0.0,
            bp_30          = dto.bp_30 or 0.0,
            bp_35          = dto.bp_35 or 0.0,
            bp_40          = dto.bp_40 or 0.0,
            bp_45          = dto.bp_45 or 0.0,
            bp_50          = dto.bp_50 or 0.0,
            bp_55          = dto.bp_55 or 0.0,
            bp_60          = dto.bp_60 or 0.0,
            bp_70          = dto.bp_70 or 0.0,
            bp_80          = dto.bp_80 or 0.0,
            bp_90          = dto.bp_90 or 0.0,
            bp_100         = dto.bp_100 or 0.0,
            bp_110         = dto.bp_110 or 0.0,
            bp_120         = dto.bp_120 or 0.0,
            bp_150         = dto.bp_150 or 0.0,
            bp_180         = dto.bp_180 or 0.0,
            bp_210         = dto.bp_210 or 0.0,
            bp_240         = dto.bp_240 or 0.0,
            bp_270         = dto.bp_270 or 0.0,
            bp_300         = dto.bp_300 or 0.0,
            bp_330         = dto.bp_330 or 0.0,
            bp_360         = dto.bp_360 or 0.0,
            bp_390         = dto.bp_390 or 0.0,
            bp_420         = dto.bp_420 or 0.0,
            bp_450         = dto.bp_450 or 0.0,
            bp_480         = dto.bp_480 or 0.0,
            bp_510         = dto.bp_510 or 0.0,
            bp_540         = dto.bp_540 or 0.0,
            bp_570         = dto.bp_570 or 0.0,
            bp_600         = dto.bp_600 or 0.0,
            bp_660         = dto.bp_660 or 0.0,
            bp_720         = dto.bp_720 or 0.0,
            bp_780         = dto.bp_780 or 0.0,
            bp_840         = dto.bp_840 or 0.0,
            bp_900         = dto.bp_900 or 0.0,
            bp_960         = dto.bp_960 or 0.0,
            bp_1020        = dto.bp_1020 or 0.0,
            bp_1080        = dto.bp_1080 or 0.0,
            bp_1140        = dto.bp_1140 or 0.0,
            bp_1200        = dto.bp_1200 or 0.0,
            bp_1320        = dto.bp_1320 or 0.0,
            bp_1440        = dto.bp_1440 or 0.0,
            bp_1560        = dto.bp_1560 or 0.0,
            bp_1680        = dto.bp_1680 or 0.0,
            bp_1800        = dto.bp_1800 or 0.0,
            bp_1920        = dto.bp_1920 or 0.0,
            bp_2040        = dto.bp_2040 or 0.0,
            bp_2160        = dto.bp_2160 or 0.0,
            bp_2280        = dto.bp_2280 or 0.0,
            bp_2400        = dto.bp_2400 or 0.0,
            bp_2520        = dto.bp_2520 or 0.0,
            bp_2640        = dto.bp_2640 or 0.0,
            bp_2760        = dto.bp_2760 or 0.0,
            bp_2880        = dto.bp_2880 or 0.0,
            bp_3000        = dto.bp_3000 or 0.0,
            bp_3120        = dto.bp_3120 or 0.0,
            bp_3240        = dto.bp_3240 or 0.0,
            bp_3360        = dto.bp_3360 or 0.0,
            bp_3480        = dto.bp_3480 or 0.0,
            bp_3600        = dto.bp_3600 or 0.0,
            bp_3900        = dto.bp_3900 or 0.0,
            bp_4200        = dto.bp_4200 or 0.0,
            bp_4500        = dto.bp_4500 or 0.0,
            bp_4800        = dto.bp_4800 or 0.0,
            bp_5100        = dto.bp_5100 or 0.0,
            bp_5400        = dto.bp_5400 or 0.0,
            bp_5700        = dto.bp_5700 or 0.0,
            bp_6000        = dto.bp_6000 or 0.0,
            bp_6300        = dto.bp_6300 or 0.0,
            bp_6600        = dto.bp_6600 or 0.0,
            bp_7200        = dto.bp_7200 or 0.0,
    )

    @staticmethod
    def from_ZwiftRacingAppProfileDTO(dto: Optional[ZwiftRacingAppRiderParticularsDTO]) -> "ZsunWattsPropertiesItem":
        if dto is None:
            return ZsunWattsPropertiesItem()
        return ZsunWattsPropertiesItem(
            zwift_id = dto.zwift_id if dto.zwift_id else "",
            bp_5     = dto.power.w5 if dto.power and dto.power.w5 else 0.0,
            bp_15    = dto.power.w15 if dto.power and dto.power.w15 else 0.0,
            bp_30    = dto.power.w30 if dto.power and dto.power.w30 else 0.0,
            bp_60    = dto.power.w60 if dto.power and dto.power.w60 else 0.0,
            bp_120   = dto.power.w120 if dto.power and dto.power.w120 else 0.0,
            bp_300   = dto.power.w300 if dto.power and dto.power.w300 else 0.0,
            bp_1200  = dto.power.w1200 if dto.power and dto.power.w1200 else 0.0,
    )

    @staticmethod
    def from_ZwiftPowerBestPowerDTO(dto: Optional[ZwiftPowerWattsOrdinatesDTO]) -> "ZsunWattsPropertiesItem":
        if dto is None:
            return ZsunWattsPropertiesItem()

        xx = dto.efforts.get("90days", []) if dto.efforts else []

        effortItems = [EffortItem.from_dataTransferObject(effort) for effort in xx]

        cp_data = {effort.x: float(effort.y) for effort in effortItems if effort.x and effort.y}

        flattened = ZsunWattsPropertiesItem()

        # flattened.zwift_id = dto.zwift_id if dto.zwift_id else "" #N.B. no such data exists in the DTO. we get it later from the file name

        flattened.import_x_y_ordinates(cp_data)

        return flattened


