from dataclasses import dataclass

@dataclass
class PowerItem:
    wkg5: float = 0.0
    wkg15: float = 0.0
    wkg30: float = 0.0
    wkg60: float = 0.0
    wkg120: float = 0.0
    wkg300: float = 0.0
    wkg1200: float = 0.0
    w5: float = 0
    w15: float = 0
    w30: float = 0
    w60: float = 0
    w120: float = 0
    w300: float = 0
    w1200: float = 0
    CP: float = 0.0  # Critical Power
    AWC: float = 0.0  # Anaerobic Work Capacity
    compoundScore: float = 0.0  # Compound score
    powerRating: float = 0.0  # Power rating

    @staticmethod
    def from_dataTransferObject(dto: ZwiftRacingAppProfileDTO.PowerDTO) -> "PowerItem":
        return PowerItem(
            wkg5=dto.wkg5 or 0.0,
            wkg15=dto.wkg15 or 0.0,
            wkg30=dto.wkg30 or 0.0,
            wkg60=dto.wkg60 or 0.0,
            wkg120=dto.wkg120 or 0.0,
            wkg300=dto.wkg300 or 0.0,
            wkg1200=dto.wkg1200 or 0.0,
            w5=dto.w5 or 0,
            w15=dto.w15 or 0,
            w30=dto.w30 or 0,
            w60=dto.w60 or 0,
            w120=dto.w120 or 0,
            w300=dto.w300 or 0,
            w1200=dto.w1200 or 0,
            CP=dto.CP or 0.0,
            AWC=dto.AWC or 0.0,
            compoundScore=dto.compoundScore or 0.0,
            powerRating=dto.powerRating or 0.0,
        )

    def to_dataTransferObject(self) -> ZwiftRacingAppProfileDTO.PowerDTO:
        return ZwiftRacingAppProfileDTO.PowerDTO(
            wkg5=self.wkg5,
            wkg15=self.wkg15,
            wkg30=self.wkg30,
            wkg60=self.wkg60,
            wkg120=self.wkg120,
            wkg300=self.wkg300,
            wkg1200=self.wkg1200,
            w5=self.w5,
            w15=self.w15,
            w30=self.w30,
            w60=self.w60,
            w120=self.w120,
            w300=self.w300,
            w1200=self.w1200,
            CP=self.CP,
            AWC=self.AWC,
            compoundScore=self.compoundScore,
            powerRating=self.powerRating,
        )
