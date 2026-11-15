from dataclasses import dataclass

from team_member_dto import TeamMemberDTO
from zwift_id_base import ZwiftIdBase


@dataclass
class TeamMemberItem(ZwiftIdBase):
    rider_name: str = ""
    team_name: str = ""

    @staticmethod
    def to_dataTransferObject(item: "TeamMemberItem | None") -> TeamMemberDTO:
        if item is None:
            return TeamMemberDTO()
        return TeamMemberDTO(
            zwift_id=item.zwift_id,
            rider_name=item.rider_name,
            team_name=item.team_name,
        )

    @staticmethod
    def from_dataTransferObject(dto: "TeamMemberDTO | None") -> "TeamMemberItem":
        if dto is None:
            return TeamMemberItem()
        item = TeamMemberItem()
        item.zwift_id = dto.zwift_id
        item.rider_name = dto.rider_name
        item.team_name = dto.team_name
        return item
