from dataclasses import dataclass

from rider_aliases_dto import RiderAliasesDTO
from zwift_id_base import ZwiftIdBase


@dataclass
class RiderAliasesItem(ZwiftIdBase):
    alias_rider_stats_item: str = ""
    alias_rider_compute_item: str = ""
    zwift_country_code3: str = ""
    alias_zwift_first_name: str = ""
    alias_zwift_last_name: str = ""
    alias_zwiftpower: str = ""
    alias_zwiftracing_app: str = ""

    @staticmethod
    def to_dataTransferObject(item: "RiderAliasesItem | None") -> RiderAliasesDTO:
        if item is None:
            return RiderAliasesDTO()
        return RiderAliasesDTO(
            zwift_id=item.zwift_id,
            alias_rider_stats_item=item.alias_rider_stats_item,
            alias_rider_compute_item=item.alias_rider_compute_item,
            zwift_country_code3=item.zwift_country_code3,
            alias_zwift_first_name=item.alias_zwift_first_name,
            alias_zwift_last_name=item.alias_zwift_last_name,
            alias_zwiftpower=item.alias_zwiftpower,
            alias_zwiftracing_app=item.alias_zwiftracing_app,
        )

    @staticmethod
    def from_dataTransferObject(dto: "RiderAliasesDTO | None") -> "RiderAliasesItem":
        if dto is None:
            return RiderAliasesItem()
        item = RiderAliasesItem()
        item.zwift_id = dto.zwift_id
        item.alias_rider_stats_item = dto.alias_rider_stats_item
        item.alias_rider_compute_item = dto.alias_rider_compute_item
        item.zwift_country_code3 = dto.zwift_country_code3
        item.alias_zwift_first_name = dto.alias_zwift_first_name
        item.alias_zwift_last_name = dto.alias_zwift_last_name
        item.alias_zwiftpower = dto.alias_zwiftpower
        item.alias_zwiftracing_app = dto.alias_zwiftracing_app
        return item
