from pydantic import BaseModel
from typing import List
from models01 import *
from models02 import *

class ActionPeriodWithinRotation(BaseModel):
    index : int = 1
    duration: float = 0.0
    speed: float = 0.0
    power_limit_factor : float = 1.0
    rider_actions: List[RiderQuantumOfEffort] = []

    @staticmethod
    def create(index : int, riders: List[ZwiftRider], duration: int, speed: float, power_ceiling_factor : float, positions: List[int]) -> 'ActionPeriodWithinRotation':
        
        rider_actions = [RiderQuantumOfEffort.create(rider, duration, speed, 0, position) for rider, position in zip(riders, positions)]

        return ActionPeriodWithinRotation(index = index, duration=duration, speed=speed, power_limit_factor=power_ceiling_factor, rider_actions=rider_actions)


    def find_overworked_riders(self) -> List[RiderQuantumOfEffort]:
        
        return [rider_action for rider_action in self.rider_actions if rider_action.power_output > rider_action.rider.ftp * self.power_limit_factor]


    def actionperiod_is_too_hard(self) -> bool:
        # return false if find_riders_with_excessive_power any
        if self.find_overworked_riders():
            return False

        return True


