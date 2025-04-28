
from dataclasses import dataclass, field
from collections import defaultdict
from handy_utilities import *
from jgh_sanitise_string import sanitise_string
from zwift_profile_dto import ZwiftProfileDTO
from zwiftracingapp_profile_dto import ZwiftRacingAppProfileDTO
from zwiftpower_profile_dto import ZwiftPowerProfileDTO
from zsun_rider_item import ZwiftPower90DayBestGraphItem


@dataclass
@dataclass
class ScrapedZwiftDataRepository:
    dict_of_zwift_profileDTO: defaultdict[str, ZwiftProfileDTO] = field(default_factory=lambda: defaultdict(ZwiftProfileDTO))
    dict_of_zwiftracingapp_profileDTO: defaultdict[str, ZwiftRacingAppProfileDTO] = field(default_factory=lambda: defaultdict(ZwiftRacingAppProfileDTO))
    dict_of_zwiftpower_profileDTO: defaultdict[str, ZwiftPowerProfileDTO] = field(default_factory=lambda: defaultdict(ZwiftPowerProfileDTO))
    dict_of_zwiftpower_90daybest_graph_item: defaultdict[str, ZwiftPower90DayBestGraphItem] = field(default_factory=lambda: defaultdict(ZwiftPower90DayBestGraphItem))

    dict_of_zwift_profileDTO:               defaultdict[str, ZwiftProfileDTO]  
    dict_of_zwiftracingapp_profileDTO:      defaultdict[str, ZwiftRacingAppProfileDTO] 
    dict_of_zwiftpower_profileDTO:          defaultdict[str, ZwiftPowerProfileDTO] 
    dict_of_zwiftpower_90daybest_graph_item: defaultdict[str, ZwiftPower90DayBestGraphItem]

    def populate_repository(
        self,
        riderIDs: Optional[list[str]],
        zwift_profile_dir_path: str,
        zwiftracingapp_profile_dir_path: str,
        zwiftpower_profile_dir_path: str,
        zwiftpower_90daybest_dir_path: str
    ):
        self.dict_of_zwift_profileDTO               = read_many_zwift_profile_files_in_folder(riderIDs, zwift_profile_dir_path)
        self.dict_of_zwiftracingapp_profileDTO      = read_many_zwiftracingapp_profile_files_in_folder(riderIDs, zwiftracingapp_profile_dir_path)
        self.dict_of_zwiftpower_profileDTO          = read_many_zwiftpower_profile_files_in_folder(riderIDs, zwiftpower_profile_dir_path)
        self.dict_of_zwiftpower_90daybest_graph_item = read_many_zwiftpower_critical_power_graph_files_in_folder(riderIDs, zwiftpower_90daybest_dir_path)

            #Step 00: go through all four dicts and sanitise the names


        for key, profile in self.dict_of_zwift_profileDTO.items():
            profile.firstName = sanitise_string(profile.firstName)
            profile.lastName = sanitise_string(profile.lastName)
            self.dict_of_zwift_profileDTO[key] = profile

        for key, profile in self.dict_of_zwiftracingapp_profileDTO.items():
            profile.fullname = sanitise_string(profile.fullname)
            self.dict_of_zwiftracingapp_profileDTO[key] = profile

        for key, profile in self.dict_of_zwiftpower_profileDTO.items():
            profile.zwift_name = sanitise_string(profile.zwift_name)
            self.dict_of_zwiftpower_profileDTO[key] = profile

        for key, profile in self.dict_of_zwiftpower_90daybest_graph_item.items():
            profile.name = sanitise_string(profile.name)
            self.dict_of_zwiftpower_90daybest_graph_item[key] = profile


