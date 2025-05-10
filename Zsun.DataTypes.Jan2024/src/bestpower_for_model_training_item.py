
from dataclasses import dataclass
from bestpower_for_model_training_dto import BestPowerModelTrainingDTO

@dataclass
class BestPowerModelTrainingItem:
    zwift_id                   : str   = ""    # Zwift ID of the rider
    name                       : str   = ""    # Name of the rider
    gender                     : str   = ""    # Gender of the rider
    weight_kg                  : float = 0.0
    height_cm                  : float = 0.0
    age_years                  : float = 0.0   # Age of the rider in years
    zwift_zrs                  : float = 0.0   # Zwift racing score
    zwift_cat                  : str   = ""    # A+, A, B, C, D, E
    zwift_ftp                  : float = 0.0
    zwiftracingapp_zpFTP       : float = 0.0
    zwiftracingapp_score       : float = 0.0   # Velo score typically over 1000
    zwiftracingapp_cat_num     : int   = 0     # Velo rating 1 to 10
    zwiftracingapp_cat_name    : str   = ""    # Copper, Silver, Gold etc
    bp_5                       : float = 0.0
    bp_15                      : float = 0.0
    bp_30                      : float = 0.0
    bp_60                      : float = 0.0
    bp_180                     : float = 0.0
    bp_300                     : float = 0.0
    bp_600                     : float = 0.0
    bp_720                     : float = 0.0
    bp_900                     : float = 0.0
    bp_1200                    : float = 0.0
    bp_1800                    : float = 0.0
    bp_2400                    : float = 0.0

    @staticmethod
    def from_dataTransferObject(dto: BestPowerModelTrainingDTO) -> "BestPowerModelTrainingItem":
        return BestPowerModelTrainingItem(
            zwift_id                   = dto.zwift_id or "",
            name                       = dto.name or "",
            gender                     = dto.gender or "",
            weight_kg                  = dto.weight_kg or 0.0,
            height_cm                  = dto.height_cm or 0.0,
            age_years                  = dto.age_years or 0.0,
            zwift_zrs                  = dto.zwift_zrs or 0.0,
            zwift_cat                  = dto.zwift_cat or "",
            zwift_ftp                  = dto.zwift_ftp or 0.0,
            zwiftracingapp_zpFTP       = dto.zwiftracingapp_zpFTP or 0.0,
            zwiftracingapp_score       = dto.zwiftracingapp_score or 0.0,
            zwiftracingapp_cat_num     = dto.zwiftracingapp_cat_num or 0,
            zwiftracingapp_cat_name    = dto.zwiftracingapp_cat_name or "",
            bp_5                       = dto.bp_5 or 0.0,
            bp_15                      = dto.bp_15 or 0.0,
            bp_30                      = dto.bp_30 or 0.0,
            bp_60                      = dto.bp_60 or 0.0,
            bp_180                     = dto.bp_180 or 0.0,
            bp_300                     = dto.bp_300 or 0.0,
            bp_600                     = dto.bp_600 or 0.0,
            bp_720                     = dto.bp_720 or 0.0,
            bp_900                     = dto.bp_900 or 0.0,
            bp_1200                    = dto.bp_1200 or 0.0,
            bp_1800                    = dto.bp_1800 or 0.0,
            bp_2400                    = dto.bp_2400 or 0.0
        )

    @staticmethod
    def to_dataTransferObject(item: "BestPowerModelTrainingItem") -> BestPowerModelTrainingDTO:
        return BestPowerModelTrainingDTO(
            zwift_id                   = item.zwift_id,
            name                       = item.name,
            gender                     = item.gender,
            weight_kg                  = item.weight_kg,
            height_cm                  = item.height_cm,
            age_years                  = item.age_years,
            zwift_zrs                  = item.zwift_zrs,
            zwift_cat                  = item.zwift_cat,
            zwift_ftp                  = item.zwift_ftp,
            zwiftracingapp_zpFTP       = item.zwiftracingapp_zpFTP,
            zwiftracingapp_score       = item.zwiftracingapp_score,
            zwiftracingapp_cat_num     = item.zwiftracingapp_cat_num,
            zwiftracingapp_cat_name    = item.zwiftracingapp_cat_name,
            bp_5                       = item.bp_5,
            bp_15                      = item.bp_15,
            bp_30                      = item.bp_30,
            bp_60                      = item.bp_60,
            bp_180                     = item.bp_180,
            bp_300                     = item.bp_300,
            bp_600                     = item.bp_600,
            bp_720                     = item.bp_720,
            bp_900                     = item.bp_900,
            bp_1200                    = item.bp_1200,
            bp_1800                    = item.bp_1800,
            bp_2400                    = item.bp_2400
        )
