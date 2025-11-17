from dataclasses import dataclass
from zwift_id_base import ZwiftIdBase
from zwiftpower_profile_dto import ZwiftPowerProfileDTO

@dataclass
class ZwiftPowerProfileItem(ZwiftIdBase):
	nickname				:	str		=	""			# Nickname of the rider
	team_name				:	str		=	""			# Team name
	zftp_from_somewhere		:	float	=	0.0			# ZFTP value
	age_bracket				:	str		=	""			# Age bracket

	@staticmethod
	def from_dataTransferObject(dto: ZwiftPowerProfileDTO) -> "ZwiftPowerProfileItem":
		return ZwiftPowerProfileItem(
			zwift_id				=	dto.person_id or "",
			nickname				=	dto.nickname or "",
			team_name				=	dto.team_name or "",
			zftp_from_somewhere		=	float(dto.zftp_from_somewhere) if isinstance(dto.zftp_from_somewhere, (int, float, str)) and dto.zftp_from_somewhere else 0.0,
			age_bracket				=	dto.age_bracket or "",
		)

	@staticmethod
	def to_dataTransferObject(item: "ZwiftPowerProfileItem") -> ZwiftPowerProfileDTO:
		return ZwiftPowerProfileDTO(
			person_id				=	item.zwift_id,
			nickname				=	item.nickname,
			team_name				=	item.team_name,
			zftp_from_somewhere		=	str(item.zftp_from_somewhere) if item.zftp_from_somewhere else "0.0",
			age_bracket				=	item.age_bracket,
		)