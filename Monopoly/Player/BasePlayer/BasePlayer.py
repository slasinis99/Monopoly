from random import randint

class BasePlayer():
    def __init__(self, name) -> None:
        #Immutable Fields
        self.name = name

        #Mutable Fields
        self.bankrupt = False
        self.money = 0
        self.current_space = 0
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail = 0
        self.properties = []
        self.railroads = []
        self.utilities = []
    
    def roll_dice(self) -> tuple[int, int]:
        return (randint(1,6), randint(1,6))
    
    def should_buy_property(self, property) -> bool:
        if self.money >= property.price:
            return True
        return False
    
    def make_auction_offer(self, property, current_offer) -> int:
        if self.money < current_offer:
            return 0
        if self.money > current_offer + 1 and randint(1,4) < 4:
            return current_offer + 1
    
    def use_get_out_of_jail(self) -> bool:
        if self.get_out_of_jail > 0:
            return True
        return False
    
    def pay_out_of_jail(self) -> bool:
        if self.money >= 50:
            return True
        return False