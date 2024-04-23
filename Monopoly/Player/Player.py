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
        if self.money >= amount:
            return True
        
        colors = list(set([prop.color for prop in self.properties if prop.is_monopoly]))
        colors.sort(key=lambda x: (len([prop for prop in self.properties if prop.color == x]), min(prop.house_cost for prop in self.properties if prop.color == x)))

        did_sell = True
        while self.money < amount and did_sell == True:
            did_sell = False
            for c in colors:
                if not did_sell:
                    l = [prop for prop in self.properties if prop.color == c]
                    l.sort(key=lambda x: (-x.hotel_count, -x.house_count, x.price))
                    if l[0].hotel_count > 0:
                        l[0].hotel_count = 0
                        l[0].house_count = 4
                        self.money += l[0].hotel_cost // 2
                        did_sell = True
                        turn_log.append(f'{self.name} sold a hotel on {l[0].name} and recouped ${l[0].hotel_cost // 2}.')
                    elif l[0].house_count > 0:
                        l[0].house_count -= 1
                        self.money += l[0].house_cost // 2
                        did_sell = True
                        turn_log.append(f'{self.name} sold a house on {l[0].name} and recouped ${l[0].house_cost // 2}')
        
        #If selling houses and hotels was enough, return true
        if self.money >= amount:
            return True
        
        #Otherwise we gotta start mortgaging utilities
        props = [prop for prop in self.utilities if not prop.is_mortgaged]
        if len(props) > 0:
            props.sort(key=lambda x: x.mortgage_value)
            did_sell = True
            while self.money < amount and did_sell == True:
                did_sell = False
                for p in props:
                    if not did_sell:
                        p.is_mortgaged = True
                        self.money += p.mortgage_value
                        turn_log.append(f'{self.name} mortgaged {p.name} and recouped ${p.mortgage_value}.')
                        did_sell = True
        
        if self.money >= amount:
            return True
        
        #Otherwise we gotta start mortgaging railroads
        props = [prop for prop in self.railroads if not prop.is_mortgaged]
        if len(props) > 0:
            props.sort(key=lambda x: x.mortgage_value)
            did_sell = True
            while self.money < amount and did_sell == True:
                did_sell = False
                for p in props:
                    if not did_sell:
                        p.is_mortgaged = True
                        self.money += p.mortgage_value
                        turn_log.append(f'{self.name} mortgaged {p.name} and recouped ${p.mortgage_value}.')
                        did_sell = True

        #Otherwise we gotta start mortgaging properties
        props = [prop for prop in self.properties if not prop.is_mortgaged]
        if len(props) > 0:
            props.sort(key=lambda x: x.mortgage_value)
            did_sell = True
            while self.money < amount and did_sell == True:
                did_sell = False
                for p in props:
                    if not did_sell:
                        p.is_mortgaged = True
                        self.money += p.mortgage_value
                        turn_log.append(f'{self.name} mortgaged {p.name} and recouped ${p.mortgage_value}.')
                        did_sell = True

        if self.money >= amount:
            return True

        #Otherwise We are SOL
        return False