from .BasePlayer import BasePlayer
from random import randint

class AI_J(BasePlayer):
    def roll_dice(self, turn_log: list[str]) -> tuple[int, int]:
        return super().roll_dice(turn_log)
    
    def should_buy_property(self, property) -> bool:
        if self.money >= property.price:
            return True
        return False
    
    def should_buy_house(self, property) -> bool:
        return super().should_buy_house(property)
    
    def should_buy_hotel(self, property) -> bool:
        return super().should_buy_hotel(property)
    
    def use_get_out_of_jail(self, board) -> bool:
        if board[16].is_monopoly and not board[16].owner is self or board[24].is_monopoly and not board[24].owner is self:
            return False
        if self.get_out_of_jail > 0:
            return True
        return False
    
    
    def pay_out_of_jail(self, board) -> bool:
        if board[16].is_monopoly and not board[16].owner is self or board[24].is_monopoly and not board[24].owner is self:
            return False
        if self.money >= 50:
            return True
        return False
    
    def make_auction_offer(self, property, current_offer) -> int:
        if current_offer + 1 > self.money:
            return 0
        if property.type == 'property':
            away = 3 - len([p for p in self.properties if p.color == property.color])
        else:
            away = -1
        if away == 2:
            return min(current_offer + 50, 2*property.price, self.money)
        elif away == 1:
            return min(current_offer + 100, self.money)
        else:
            return min(current_offer + randint(1, 10), current_offer + 1, self.money)
            
    
    def liquidate(self, amount: int, turn_log: list[str]) -> bool:
        return super().liquidate(amount, turn_log)
    
class AI_G(BasePlayer):
    def should_buy_property(self, property) -> bool:
        if self.money >= property.price + 500:
            return True
        return False
    
    def buy_back_mortgage(self, property) -> bool:
        if self.money >= property.mortgage_value + 500:
            return True
        return False
    
    def should_buy_house(self, property) -> bool:
        if self.money >= property.house_cost + 500:
            return True
        return False
    
    def should_buy_hotel(self, property) -> bool:
        if self.money >= property.hotel_cost + 500:
            return True
        return False
    
    def use_get_out_of_jail(self, board) -> bool:
        if self.get_out_of_jail > 0:
            return True
        else:
            return False
    
    def pay_out_of_jail(self, board) -> bool:
        return False
    
    def make_auction_offer(self, property, current_offer) -> int:
        if current_offer + 1 > self.money or current_offer >= 0.3*property.price:
            return 0
        return min(current_offer + randint(1,10), 0.3*property.price, self.money)