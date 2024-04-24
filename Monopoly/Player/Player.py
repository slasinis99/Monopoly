from .BasePlayer import BasePlayer

class AI_Stephen(BasePlayer):
    def roll_dice(self, turn_log: list[str]) -> tuple[int, int]:
        return super().roll_dice(turn_log)
    
    def should_buy_property(self, property) -> bool:
        return super().should_buy_property(property)
    
    def should_buy_house(self, property) -> bool:
        return super().should_buy_house(property)
    
    def should_buy_hotel(self, property) -> bool:
        return super().should_buy_hotel(property)
    
    def use_get_out_of_jail(self) -> bool:
        return super().use_get_out_of_jail()
    
    def pay_out_of_jail(self) -> bool:
        return super().pay_out_of_jail()
    
    def make_auction_offer(self, property, current_offer) -> int:
        return super().make_auction_offer(property, current_offer)
    
    def liquidate(self, amount: int, turn_log: list[str]) -> bool:
        return super().liquidate(amount, turn_log)