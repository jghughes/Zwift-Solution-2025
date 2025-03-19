from pydantic import BaseModel
from typing import List
from zwiftrider_item import ZwiftRiderItem
from zwiftrider_workload import TttRiderWorkLoad

class TttWorkPeriod(BaseModel):
    index : int = 1
    duration: float = 0.0
    speed: float = 0.0
    power_limit_factor : float = 1.0
    rider_workloads: List[TttRiderWorkLoad] = []

    @staticmethod
    def create(index : int, riders: List[ZwiftRiderItem], duration: int, speed: float, power_ceiling_factor : float, positions: List[int]) -> 'TttWorkPeriod':
        
        rider_workloads = [TttRiderWorkLoad.create(rider, duration, speed, position) for rider, position in zip(riders, positions)]

        return TttWorkPeriod(index = index, duration=duration, speed=speed, power_limit_factor=power_ceiling_factor, rider_workloads=rider_workloads)


    def find_overworked_riders(self) -> List[TttRiderWorkLoad]:
        
        return [rider_action for rider_action in self.rider_workloads if rider_action.power_output > rider_action.rider.ftp * self.power_limit_factor]


    def actionperiod_is_too_hard(self) -> bool:

        if self.find_overworked_riders():
            return False

        return True


