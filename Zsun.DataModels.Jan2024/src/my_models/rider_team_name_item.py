
from dataclasses import dataclass

from rider_team_name_dto import RiderTeamNameDTO
from zwift_id_base import ZwiftIdBase

# this domain model is instantiated in model_builders.py

@dataclass
class RiderTeamNameItem(ZwiftIdBase):
	full_rider_name	:	str		=	""
	team_name		:	str		=	""

	@staticmethod
	def to_dataTransferObject(item: "RiderTeamNameItem | None") -> RiderTeamNameDTO:
		if item is None:
			return RiderTeamNameDTO()
		return RiderTeamNameDTO(
			zwift_id			= item.zwift_id,
			full_rider_name		= item.full_rider_name,
			team_name			= item.team_name,
		)

	@staticmethod
	def from_dataTransferObject(dto: RiderTeamNameDTO | None) -> "RiderTeamNameItem":
		if dto is None:
			return RiderTeamNameItem()
		item = RiderTeamNameItem()
		item.zwift_id			= dto.zwift_id
		item.full_rider_name	= dto.full_rider_name
		item.team_name			= dto.team_name
		return item

