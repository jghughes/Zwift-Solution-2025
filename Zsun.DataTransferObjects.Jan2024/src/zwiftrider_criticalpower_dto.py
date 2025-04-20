# Local application imports
from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator
from typing import Optional
from jgh_read_write import *
from jgh_serialization import *

# Define the serialization alias map
serialization_alias_map: dict[str, str] = {
    "cp_1": "cp_1",
    "cp_2": "cp_2",
    "cp_3": "cp_3",
    "cp_4": "cp_4",
    "cp_6": "cp_6",
    "cp_7": "cp_7",
    "cp_8": "cp_8",
    "cp_9": "cp_9",
    "cp_10": "cp_10",
    "cp_11": "cp_11",
    "cp_13": "cp_13",
    "cp_14": "cp_14",
    "cp_16": "cp_16",
    "cp_17": "cp_17",
    "cp_18": "cp_18",
    "cp_19": "cp_19",
    "cp_21": "cp_21",
    "cp_22": "cp_22",
    "cp_23": "cp_23",
    "cp_24": "cp_24",
    "cp_25": "cp_25",
    "cp_26": "cp_26",
    "cp_27": "cp_27",
    "cp_28": "cp_28",
    "cp_29": "cp_29",
    "cp_35": "cp_35",
    "cp_40": "cp_40",
    "cp_45": "cp_45",
    "cp_50": "cp_50",
    "cp_55": "cp_55",
    "cp_70": "cp_70",
    "cp_80": "cp_80",
    "cp_100": "cp_100",
    "cp_110": "cp_110",
    "cp_150": "cp_150",
    "cp_210": "cp_210",
    "cp_240": "cp_240",
    "cp_270": "cp_270",
    "cp_330": "cp_330",
    "cp_360": "cp_360",
    "cp_390": "cp_390",
    "cp_450": "cp_450",
    "cp_480": "cp_480",
    "cp_510": "cp_510",
    "cp_540": "cp_540",
    "cp_570": "cp_570",
    "cp_660": "cp_660",
    "cp_720": "cp_720",
    "cp_780": "cp_780",
    "cp_840": "cp_840",
    "cp_960": "cp_960",
    "cp_1020": "cp_1020",
    "cp_1080": "cp_1080",
    "cp_1140": "cp_1140",
    "cp_1320": "cp_1320",
    "cp_1560": "cp_1560",
    "cp_1680": "cp_1680",
    "cp_1920": "cp_1920",
    "cp_2040": "cp_2040",
    "cp_2160": "cp_2160",
    "cp_2280": "cp_2280",
    "cp_2520": "cp_2520",
    "cp_2640": "cp_2640",
    "cp_2760": "cp_2760",
    "cp_2880": "cp_2880",
    "cp_3120": "cp_3120",
    "cp_3240": "cp_3240",
    "cp_3360": "cp_3360",
    "cp_3480": "cp_3480",
    "cp_3900": "cp_3900",
    "cp_4200": "cp_4200",
    "cp_4800": "cp_4800",
    "cp_5100": "cp_5100",
    "cp_5700": "cp_5700",
    "cp_6000": "cp_6000",
    "cp_6300": "cp_6300",
    "cp_6600": "cp_6600",
}

# Define the validation alias choices map
validation_alias_choices_map: dict[str, AliasChoices] = {
    "cp_1": AliasChoices("cp_1"),
    "cp_2": AliasChoices("cp_2"),
    "cp_3": AliasChoices("cp_3"),
    "cp_4": AliasChoices("cp_4"),
    "cp_6": AliasChoices("cp_6"),
    "cp_7": AliasChoices("cp_7"),
    "cp_8": AliasChoices("cp_8"),
    "cp_9": AliasChoices("cp_9"),
    "cp_10": AliasChoices("cp_10"),
    "cp_11": AliasChoices("cp_11"),
    "cp_13": AliasChoices("cp_13"),
    "cp_14": AliasChoices("cp_14"),
    "cp_16": AliasChoices("cp_16"),
    "cp_17": AliasChoices("cp_17"),
    "cp_18": AliasChoices("cp_18"),
    "cp_19": AliasChoices("cp_19"),
    "cp_21": AliasChoices("cp_21"),
    "cp_22": AliasChoices("cp_22"),
    "cp_23": AliasChoices("cp_23"),
    "cp_24": AliasChoices("cp_24"),
    "cp_25": AliasChoices("cp_25"),
    "cp_26": AliasChoices("cp_26"),
    "cp_27": AliasChoices("cp_27"),
    "cp_28": AliasChoices("cp_28"),
    "cp_29": AliasChoices("cp_29"),
    "cp_35": AliasChoices("cp_35"),
    "cp_40": AliasChoices("cp_40"),
    "cp_45": AliasChoices("cp_45"),
    "cp_50": AliasChoices("cp_50"),
    "cp_55": AliasChoices("cp_55"),
    "cp_70": AliasChoices("cp_70"),
    "cp_80": AliasChoices("cp_80"),
    "cp_100": AliasChoices("cp_100"),
    "cp_110": AliasChoices("cp_110"),
    "cp_150": AliasChoices("cp_150"),
    "cp_210": AliasChoices("cp_210"),
    "cp_240": AliasChoices("cp_240"),
    "cp_270": AliasChoices("cp_270"),
    "cp_330": AliasChoices("cp_330"),
    "cp_360": AliasChoices("cp_360"),
    "cp_390": AliasChoices("cp_390"),
    "cp_450": AliasChoices("cp_450"),
    "cp_480": AliasChoices("cp_480"),
    "cp_510": AliasChoices("cp_510"),
    "cp_540": AliasChoices("cp_540"),
    "cp_570": AliasChoices("cp_570"),
    "cp_660": AliasChoices("cp_660"),
    "cp_720": AliasChoices("cp_720"),
    "cp_780": AliasChoices("cp_780"),
    "cp_840": AliasChoices("cp_840"),
    "cp_960": AliasChoices("cp_960"),
    "cp_1020": AliasChoices("cp_1020"),
    "cp_1080": AliasChoices("cp_1080"),
    "cp_1140": AliasChoices("cp_1140"),
    "cp_1320": AliasChoices("cp_1320"),
    "cp_1560": AliasChoices("cp_1560"),
    "cp_1680": AliasChoices("cp_1680"),
    "cp_1920": AliasChoices("cp_1920"),
    "cp_2040": AliasChoices("cp_2040"),
    "cp_2160": AliasChoices("cp_2160"),
    "cp_2280": AliasChoices("cp_2280"),
    "cp_2520": AliasChoices("cp_2520"),
    "cp_2640": AliasChoices("cp_2640"),
    "cp_2760": AliasChoices("cp_2760"),
    "cp_2880": AliasChoices("cp_2880"),
    "cp_3120": AliasChoices("cp_3120"),
    "cp_3240": AliasChoices("cp_3240"),
    "cp_3360": AliasChoices("cp_3360"),
    "cp_3480": AliasChoices("cp_3480"),
    "cp_3900": AliasChoices("cp_3900"),
    "cp_4200": AliasChoices("cp_4200"),
    "cp_4800": AliasChoices("cp_4800"),
    "cp_5100": AliasChoices("cp_5100"),
    "cp_5700": AliasChoices("cp_5700"),
    "cp_6000": AliasChoices("cp_6000"),
    "cp_6300": AliasChoices("cp_6300"),
    "cp_6600": AliasChoices("cp_6600"),
}

# Define the Pydantic ConfigDict
configdictV1 = ConfigDict(
    alias_generator=AliasGenerator(
        alias=None,
        serialization_alias=lambda field_name: serialization_alias_map.get(field_name, field_name),
        validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name),
    )
)

preferred_config_dict = configdictV1

class ZwiftRiderCriticalPowerDTO(BaseModel):
    """
    A data transfer object representing a Zwift rider's critical power data - derived from the data recorded on ZwiftPower.
    """
    model_config = preferred_config_dict

    zwiftid: Optional[int] = 0
    name: Optional[str] = ""
    cp_1: Optional[float] = 0.0
    cp_2: Optional[float] = 0.0
    cp_3: Optional[float] = 0.0
    cp_4: Optional[float] = 0.0
    cp_5: Optional[float] = 0.0
    cp_6: Optional[float] = 0.0
    cp_7: Optional[float] = 0.0
    cp_8: Optional[float] = 0.0
    cp_9: Optional[float] = 0.0
    cp_10: Optional[float] = 0.0
    cp_11: Optional[float] = 0.0
    cp_12: Optional[float] = 0.0
    cp_13: Optional[float] = 0.0
    cp_14: Optional[float] = 0.0
    cp_15: Optional[float] = 0.0
    cp_16: Optional[float] = 0.0
    cp_17: Optional[float] = 0.0
    cp_18: Optional[float] = 0.0
    cp_19: Optional[float] = 0.0
    cp_20: Optional[float] = 0.0
    cp_21: Optional[float] = 0.0
    cp_22: Optional[float] = 0.0
    cp_23: Optional[float] = 0.0
    cp_24: Optional[float] = 0.0
    cp_25: Optional[float] = 0.0
    cp_26: Optional[float] = 0.0
    cp_27: Optional[float] = 0.0
    cp_28: Optional[float] = 0.0
    cp_29: Optional[float] = 0.0
    cp_30: Optional[float] = 0.0
    cp_35: Optional[float] = 0.0
    cp_40: Optional[float] = 0.0
    cp_45: Optional[float] = 0.0
    cp_50: Optional[float] = 0.0
    cp_55: Optional[float] = 0.0
    cp_60: Optional[float] = 0.0
    cp_70: Optional[float] = 0.0
    cp_80: Optional[float] = 0.0
    cp_90: Optional[float] = 0.0
    cp_100: Optional[float] = 0.0
    cp_110: Optional[float] = 0.0
    cp_120: Optional[float] = 0.0
    cp_150: Optional[float] = 0.0
    cp_180: Optional[float] = 0.0
    cp_210: Optional[float] = 0.0
    cp_240: Optional[float] = 0.0
    cp_270: Optional[float] = 0.0
    cp_300: Optional[float] = 0.0
    cp_330: Optional[float] = 0.0
    cp_360: Optional[float] = 0.0
    cp_390: Optional[float] = 0.0
    cp_420: Optional[float] = 0.0
    cp_450: Optional[float] = 0.0
    cp_480: Optional[float] = 0.0
    cp_510: Optional[float] = 0.0
    cp_540: Optional[float] = 0.0
    cp_570: Optional[float] = 0.0
    cp_600: Optional[float] = 0.0
    cp_660: Optional[float] = 0.0
    cp_720: Optional[float] = 0.0
    cp_780: Optional[float] = 0.0
    cp_840: Optional[float] = 0.0
    cp_900: Optional[float] = 0.0
    cp_960: Optional[float] = 0.0
    cp_1020: Optional[float] = 0.0
    cp_1080: Optional[float] = 0.0
    cp_1140: Optional[float] = 0.0
    cp_1200: Optional[float] = 0.0
    cp_1320: Optional[float] = 0.0
    cp_1440: Optional[float] = 0.0
    cp_1560: Optional[float] = 0.0
    cp_1680: Optional[float] = 0.0
    cp_1800: Optional[float] = 0.0
    cp_1920: Optional[float] = 0.0
    cp_2040: Optional[float] = 0.0
    cp_2160: Optional[float] = 0.0
    cp_2280: Optional[float] = 0.0
    cp_2400: Optional[float] = 0.0
    cp_2520: Optional[float] = 0.0
    cp_2640: Optional[float] = 0.0
    cp_2760: Optional[float] = 0.0
    cp_2880: Optional[float] = 0.0
    cp_3000: Optional[float] = 0.0
    cp_3120: Optional[float] = 0.0
    cp_3240: Optional[float] = 0.0
    cp_3360: Optional[float] = 0.0
    cp_3480: Optional[float] = 0.0
    cp_3600: Optional[float] = 0.0
    cp_3900: Optional[float] = 0.0
    cp_4200: Optional[float] = 0.0
    cp_4500: Optional[float] = 0.0
    cp_4800: Optional[float] = 0.0
    cp_5100: Optional[float] = 0.0
    cp_5400: Optional[float] = 0.0
    cp_5700: Optional[float] = 0.0
    cp_6000: Optional[float] = 0.0
    cp_6300: Optional[float] = 0.0
    cp_6600: Optional[float] = 0.0
    cp_7200: Optional[float] = 0.0
    critical_power          : Optional[float] = 0.0
    anaerobic_work_capacity : Optional[float] = 0.0
    inverse_coefficient     : Optional[float] = 0.0
    inverse_exponent        : Optional[float] = 0.0
    model_applied           : Optional[str] = ""
    generated               : Optional[str] = ""

