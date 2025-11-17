from typing import List, Dict
from pydantic import BaseModel, RootModel

# this class belongs to me, and at the time of writing it is not exported/imported,
# so I don't need the paraphenalia for pydantic validation_alias_choices_map, etc

class ZwiftPowerFlattened90DayWattsDTO(BaseModel):
    zwift_id: str = ""
    bp_1    : float = 0.0
    bp_2    : float = 0.0
    bp_3    : float = 0.0
    bp_4    : float = 0.0
    bp_5    : float = 0.0
    bp_6    : float = 0.0
    bp_7    : float = 0.0
    bp_8    : float = 0.0
    bp_9    : float = 0.0
    bp_10   : float = 0.0
    bp_11   : float = 0.0
    bp_12   : float = 0.0
    bp_13   : float = 0.0
    bp_14   : float = 0.0
    bp_15   : float = 0.0
    bp_16   : float = 0.0
    bp_17   : float = 0.0
    bp_18   : float = 0.0
    bp_19   : float = 0.0
    bp_20   : float = 0.0
    bp_21   : float = 0.0
    bp_22   : float = 0.0
    bp_23   : float = 0.0
    bp_24   : float = 0.0
    bp_25   : float = 0.0
    bp_26   : float = 0.0
    bp_27   : float = 0.0
    bp_28   : float = 0.0
    bp_29   : float = 0.0
    bp_30   : float = 0.0
    bp_35   : float = 0.0
    bp_40   : float = 0.0
    bp_45   : float = 0.0
    bp_50   : float = 0.0
    bp_55   : float = 0.0
    bp_60   : float = 0.0
    bp_70   : float = 0.0
    bp_80   : float = 0.0
    bp_90   : float = 0.0
    bp_100  : float = 0.0
    bp_110  : float = 0.0
    bp_120  : float = 0.0
    bp_150  : float = 0.0
    bp_180  : float = 0.0
    bp_210  : float = 0.0
    bp_240  : float = 0.0
    bp_270  : float = 0.0
    bp_300  : float = 0.0
    bp_330  : float = 0.0
    bp_360  : float = 0.0
    bp_390  : float = 0.0
    bp_420  : float = 0.0
    bp_450  : float = 0.0
    bp_480  : float = 0.0
    bp_510  : float = 0.0
    bp_540  : float = 0.0
    bp_570  : float = 0.0
    bp_600  : float = 0.0
    bp_660  : float = 0.0
    bp_720  : float = 0.0
    bp_780  : float = 0.0
    bp_840  : float = 0.0
    bp_900  : float = 0.0
    bp_960  : float = 0.0
    bp_1020 : float = 0.0
    bp_1080 : float = 0.0
    bp_1140 : float = 0.0
    bp_1200 : float = 0.0
    bp_1320 : float = 0.0
    bp_1440 : float = 0.0
    bp_1560 : float = 0.0
    bp_1680 : float = 0.0
    bp_1800 : float = 0.0
    bp_1920 : float = 0.0
    bp_2040 : float = 0.0
    bp_2160 : float = 0.0
    bp_2280 : float = 0.0
    bp_2400 : float = 0.0
    bp_2520 : float = 0.0
    bp_2640 : float = 0.0
    bp_2760 : float = 0.0
    bp_2880 : float = 0.0
    bp_3000 : float = 0.0
    bp_3120 : float = 0.0
    bp_3240 : float = 0.0
    bp_3360 : float = 0.0
    bp_3480 : float = 0.0
    bp_3600 : float = 0.0
    bp_3900 : float = 0.0
    bp_4200 : float = 0.0
    bp_4500 : float = 0.0
    bp_4800 : float = 0.0
    bp_5100 : float = 0.0
    bp_5400 : float = 0.0
    bp_5700 : float = 0.0
    bp_6000 : float = 0.0
    bp_6300 : float = 0.0
    bp_6600 : float = 0.0
    bp_7200 : float = 0.0


class ZwiftPower90DayWattsDTODictModel(RootModel[Dict[str, ZwiftPowerFlattened90DayWattsDTO]]):
    pass

class ZwiftPower90DayWattsDTOListModel(RootModel[List[ZwiftPowerFlattened90DayWattsDTO]]):
    pass
