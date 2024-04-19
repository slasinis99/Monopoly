from __future__ import annotations
import path
import csv
from random import shuffle
from time import sleep

DIR_CHANCE = f'{path.Path(__file__).abspath().parent}\\Data\\chance.csv'
DIR_COMMCHEST = f'{path.Path(__file__).abspath().parent}\\Data\\communitychest.csv'
DIR_PROPERTIES = f'{path.Path(__file__).abspath().parent}\\Data\\properties.csv' 
DIR_RAILROADS = f'{path.Path(__file__).abspath().parent}\\Data\\railroads.csv'
DIR_UTILITIES = f'{path.Path(__file__).abspath().parent}\\Data\\utilities.csv'

class MonopolyBoard():
    def __init__(self) -> None:
        self.active = False
        self.current_turn = 0
        self.players = []

class Property():
    def __init__(self, name: str, color: str, price: int, rent, one_ouse, two_house, three_house, four_house, hotel, mortgage_value: int, house_cost: int, hotel_cost: int) -> None:
        #Immutable Fields
        self.name = name
        self.color = color
        self.price = price
        self.rents = [rent, one_ouse, two_house, three_house, four_house, hotel]
        self.mortgage_value = mortgage_value
        self.house_cost = house_cost
        self.hotel_cost = hotel_cost

        #Mutable Fields
        self.owner = None
        self.house_count = 0
        self.hotel_count = 0
        self.is_mortgaged = False
        self.is_monopoly = False

    def __str__(self) -> str:
        s = f' {"-"*100} \n {f" {self.name} ({self.color}) ":-^100} \n {"-"*100} \n'
        #Owner and Price
        if self.owner is None:
            s += f'|{f"Owner: {self.owner}": ^100}|\n'
        else:
            s += f'|{f"Owner: {self.owner.name}": ^50}{f"Price: {self.price}": ^50}|\n'

        if not self.owner is None:
            #Houses and Rent
            if self.hotel_count > 0:
                s += f'|{f"Hotels: {self.hotel_count}": ^50}{f"Rent: {self.rents[5]}": ^50}|\n'
            else:
                s += f'|{f"Houses: {self.house_count}": ^50}'
                if self.house_count == 0 and self.is_monopoly:
                    s += f'{f"Rent: {2*self.rents[0]}": ^50}|\n'
                else:
                    s += f'{f"Rent: {self.rents[self.house_count]}": ^50}|\n'

            #Mortgage and Monopoly
            if self.is_mortgaged:
                s += f'|{f"Currently Mortgaged": ^50}'
            else:
                s += f'|{f"Mortgage: {self.mortgage_value}": ^50}'
            if self.is_monopoly:
                s += f'{"Has a Monopoly": ^50}|\n'
            else:
                s += f'{"Not a Monopoly": ^50}|\n'
        else:
            #Nothing and Base Rent
            s += f'|{" "*50}{f"Rent: {self.rents[0]}": ^50}|\n'
            #Price and 1 house rent
            s += f'|{f"Price to Own: {self.price}": ^50}{f"1 House: {self.rents[1]}": ^50}|\n'
            #Mortgage value and 2 house rent
            s += f'|{f"Mortgage Value: {self.mortgage_value}": ^50}{f"2 Houses: {self.rents[2]}": ^50}|\n'
            #House cost and 3 house rent
            s += f'|{f"House Cost: {self.house_cost}": ^50}{f"3 Houses: {self.rents[3]}": ^50}|\n'
            #Hotel Cost and 4 house rent
            s += f'|{f"Hotel Cost: {self.hotel_cost}": ^50}{f"4 Houses: {self.rents[4]}": ^50}|\n'
            #Nothing and Hotel rent
            s += f'|{" "*50}{f"Hotel: {self.rents[5]}": ^50}|\n'

        s += f' {"-"*100} '
        return s

class RailRoad():
    def __init__(self, name: str, price: int, rent_one, rent_two, rent_three, rent_four, mortgage_value: int) -> None:
        #Immutable Fields
        self.name = name
        self.price = price
        self.rents = [rent_one, rent_two, rent_three, rent_four]
        self.mortgage_value = mortgage_value

        #Mutable Fields
        self.owner = None
        self.is_mortgaged = False
        self.amount_owned = 0

    def __str__(self) -> str:
        s = f' {"-"*100} \n {f" {self.name} ":-^100} \n {"-"*100} \n'
        #Owner and Price
        if self.owner is None:
            s += f'|{f"Owner: {self.owner}": ^100}|\n'
        else:
            s += f'|{f"Owner: {self.owner.name}": ^50}{f"Price: {self.price}": ^50}|\n'

        if not self.owner is None:
            s += f'|{f"Amount Owned: {self.amount_owned}": ^50}{f"Rent: {self.rents[self.amount_owned-1]}": ^50}|\n'

            #Mortgage and Monopoly
            if self.is_mortgaged:
                s += f'|{f"Currently Mortgaged": ^50}'
            else:
                s += f'|{f"Mortgage: {self.mortgage_value}": ^50}'
            if self.amount_owned == 4:
                s += f'{"Has a Monopoly": ^50}|\n'
            else:
                s += f'{"Not a Monopoly": ^50}|\n'
        else:
            #Nothing and Base rent
            s += f'|{" "*50}{f"Rent: {self.rents[0]}": ^50}|\n'
            #Price and 2 owned rent
            s += f'|{f"Price to Own: {self.price}": ^50}{f"2 Owned: {self.rents[1]}": ^50}|\n'
            #Mortgage Value and 3 owned rent
            s += f'|{f"Mortgage Value: {self.mortgage_value}": ^50}{f"3 Owned: {self.rents[2]}": ^50}|\n'
            #Nothing and 4 owned rent
            s += f'|{" "*50}{f"4 Owned: {self.rents[3]}": ^50}|\n'
        
        s += f' {"-"*100} '
        return s

class Utility():
    def __init__(self, name: str, price: str, rent_one: int, rent_two: int, mortgage_value: int) -> None:
        #Immutable Fields
        self.name = name
        self.price = price
        self.rents = [rent_one, rent_two]
        self.mortgage_value = mortgage_value

        #Mutable Fields
        self.owner: Player = None
        self.is_mortgaged = False
        self.amount_owned = 0

    def __str__(self) -> str:
        s = f' {"-"*100}\n {f" {self.name} ":-^100}\n {"-"*100}\n'

        if not self.owner is None:
            s += f'|{f"Owner: {self.owner.name}": ^100}|\n'
            s += f'|{f"Amount Owned: {self.amount_owned}": ^50}{f"Rent: {self.rents[self.amount_owned-1]} x Dice Roll": ^50}|\n'
            if self.is_mortgaged:
                s += f'|{f"Is Mortgaged": ^50}'
            else:
                s += f'|{f"Mortgage Value: {self.mortgage_value}": ^50}'
            if self.amount_owned == 2:
                s += f'{f"Has a Monopoly": ^50}|\n'
            else:
                s += f'{f"Not a Monopoly": ^50}|\n'
        else:
            s += f'|{f"Owner: {self.owner}": ^50}{f"Price: {self.price}": ^50}|\n'
            s += f'|{f"Mortgage Value: {self.mortgage_value}": ^50}{f"Rent: {self.rents[0]} x Dice Roll": ^50}|\n'
            s += f'|{" "*50}{f"2 Owned: {self.rents[1]} x Dice Roll": ^50}|\n'
        s += f' {"-"*100} '
        return s


class CommunityChest():
    def __init__(self) -> None:
        self.unused_cards = []
        self.used_cards = []

        #Load all Community Chest Cards Into the List
        with open(DIR_COMMCHEST, 'r') as file:
            itr = csv.reader(file)
            next(itr)
            for row in itr:
                self.unused_cards.append(CommunityChestCard(str(row[0]), str(row[1]), int(row[2]), str(row[3]), str(row[4])))
        
        #Shuffle the List
        shuffle(self.unused_cards)
    
    def draw(self) -> CommunityChestCard:
        result = self.unused_cards[-1]
        self.used_cards.append(result)
        self.unused_cards.pop()
        if len(self.unused_cards) == 0:
            self.unused_cards = self.used_cards
            self.used_cards = []
            shuffle(self.unused_cards)
        return result
        

class CommunityChestCard():
    def __init__(self, payee, payer, amount, goto, text) -> None:
        self.payee = payee
        self.payer = payer
        self.amount = amount
        self.goto = goto
        self.text = text

    def __str__(self) -> str:
        return self.text

class Chance():
    def __init__(self) -> None:
        self.unused_cards = []
        self.used_cards = []

        #Load all Community Chest Cards Into the List
        with open(DIR_CHANCE, 'r') as file:
            itr = csv.reader(file)
            next(itr)
            for row in itr:
                self.unused_cards.append(ChanceCard(str(row[0]), str(row[1]), int(row[2]), str(row[3]), int(row[4]), str(row[5])))
        
        #Shuffle the List
        shuffle(self.unused_cards)
    
    def draw(self) -> ChanceCard:
        result = self.unused_cards[-1]
        self.used_cards.append(result)
        self.unused_cards.pop()
        if len(self.unused_cards) == 0:
            self.unused_cards = self.used_cards
            self.used_cards = []
            shuffle(self.unused_cards)
        return result

class ChanceCard():
    def __init__(self, payee, payer, amount, goto, collect, text) -> None:
        self.payee = payee
        self.payer = payer
        self.amount = amount
        self.goto = goto
        self.collect = collect
        self.text = text

    def __str__(self) -> str:
        return self.text

class PlayerList():
    def __init__(self, l: list[Player]) -> None:
        self.l = l
        self.name_to_player = {}
        self.size = len(l)
        for p in l:
            self.name_to_player[p.name] = p
    
    def __len__(self) -> int:
        return self.size
    
    def __iter__(self):
        for p in self.l:
            yield p
    
    def __getitem__(self, k: int | str) -> Player:
        result = None
        if isinstance(k, int):
            result = self.l[k]
        elif isinstance(k,str):
            result = self.name_to_player.get(k)
        if result is None:
            raise KeyError(f'Invalid Key: {k}')
        return result

class Player():
    def __init__(self, name) -> None:
        #Immutable Fields
        self.name = name

        #Mutable Fields
        self.money = 0
        self.current_space = 0
        self.properties = []
        self.railroads = []
        self.utilities = []

p = Player('Stephen')
pr = Property('Marvin Gardens', 'Yellow', 280, 24, 120, 360, 850, 1025, 1200, 140, 150, 150)
rr = RailRoad('Reading Railroad', 200, 25, 50, 100, 200, 100)
ur = Utility('Electric Company', 150, 4, 10, 75)
ur.owner = p
ur.amount_owned = 2

chest = Chance()
for _ in range(32):
    print(chest.draw())