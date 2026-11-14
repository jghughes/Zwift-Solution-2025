from dataclasses import dataclass

from simple_rider_dto import SimpleRiderDTO
from zwift_id_base import ZwiftIdBase


@dataclass
class SimpleRiderItem(ZwiftIdBase):
    rider_name: str = ""
    team_name: str = ""

    @staticmethod
    def to_dataTransferObject(item: "SimpleRiderItem | None") -> "SimpleRiderDTO":
        if item is None:
            return SimpleRiderDTO()
        return SimpleRiderDTO(
            zwift_id=item.zwift_id,
            rider_name=item.rider_name,
            team_name=item.team_name,
        )

    @staticmethod
    def from_dataTransferObject(dto: "SimpleRiderDTO | None") -> "SimpleRiderItem":
        if dto is None:
            return SimpleRiderItem()
        item = SimpleRiderItem()
        item.zwift_id = dto.zwift_id
        item.rider_name = dto.rider_name
        item.team_name = dto.team_name
        return item
