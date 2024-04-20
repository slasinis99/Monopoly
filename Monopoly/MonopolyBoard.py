from __future__ import annotations
import path
import csv
from random import shuffle
from time import sleep

from Player import BasePlayer, AI_Stephen

DIR_CHANCE = f'{path.Path(__file__).abspath().parent}\\Data\\chance.csv'
DIR_COMMCHEST = f'{path.Path(__file__).abspath().parent}\\Data\\communitychest.csv'
DIR_PROPERTIES = f'{path.Path(__file__).abspath().parent}\\Data\\properties.csv' 
DIR_RAILROADS = f'{path.Path(__file__).abspath().parent}\\Data\\railroads.csv'
DIR_UTILITIES = f'{path.Path(__file__).abspath().parent}\\Data\\utilities.csv'

class AIException(Exception):
    pass

class MonopolyBoard():
    def __init__(self, players: PlayerList) -> None:
        #Keep track of whether or not an active game is going on
        self.active = False

        #Keep a log of each turn in a dictionary
        self.game_log = {}

        #Current turn we are on. Increments at the start of a turn
        self.current_turn = 0

        #List of the Player objects in the game
        self.players = players

        #List of spaces, can be property, railroad, utility, or text with instructions
        self.spaces = []

        #Keep track of the free parking money
        self.park_money = 0

        #Create the universal spaces for community chest and chance
        space_commchest = CommunityChest()
        space_chance = Chance()

        #Create the list of all regular properties
        p_list = []
        with open(DIR_PROPERTIES, 'r') as file:
            itr = csv.reader(file)
            next(itr)
            for r in itr:
                p_list.append(Property(str(r[0]), str(r[1]), int(r[2]), int(r[3]), int(r[4]), int(r[5]), int(r[6]), int(r[7]), int(r[8]), int(r[9]), int(r[10]), int(r[11])))
        
        #Create the list of all railroads
        r_list = []
        with open(DIR_RAILROADS, 'r') as file:
            itr = csv.reader(file)
            next(itr)
            for r in itr:
                r_list.append(RailRoad(str(r[0]), int(r[1]), int(r[2]), int(r[3]), int(r[4]), int(r[5]), int(r[6])))
        
        #Create the list of all utilities
        u_list = []
        with open(DIR_UTILITIES, 'r') as file:
            itr = csv.reader(file)
            next(itr)
            for r in itr:
                u_list.append(Utility(str(r[0]), int(r[1]), int(r[2]), int(r[3]), int(r[4])))
        
        #Now we can actually create the list of all spaces
        self.board = ['go', p_list[0], space_commchest, p_list[1], 'income-tax', r_list[0], p_list[2], space_chance, p_list[3], p_list[4], 'jail', p_list[5], u_list[0], p_list[6], p_list[7], r_list[1], p_list[8], space_commchest, p_list[9], p_list[10], 'park', p_list[11], space_chance, p_list[12], p_list[13], r_list[2], p_list[14], p_list[15], u_list[1], p_list[16], 'goto-jail', p_list[17], p_list[18], space_commchest, p_list[19], r_list[3], space_chance, p_list[20], 'luxury-tax', p_list[21]]

    def validate_roll(self, p, roll):
        if not isinstance(roll, tuple):
            raise AIException(f'AI-({p.name}) did not return a tuple when rolling dice!')
        if not len(roll) == 2:
            raise AIException(f'AI-({p.name}) did not roll exactly two dice')
        if not isinstance(roll[0], int) or not isinstance(roll[1], int):
            raise AIException(f'AI-({p.name}) somehow rolled a non-integer value!')
        if roll[0] < 1 or roll[0] > 6:
            raise AIException(f'AI-({p.name}) rolled a {roll[0]} which is not feasible!')
        if roll[1] < 1 or roll[1] > 6:
            raise AIException(f'AI-({p.name}) rolled a {roll[1]} which is not feasible!')

    def start_game(self):
        #Reset variables in order to have a fresh start
        pass

    def turn(self):
        #First we increment the number of turns performed, we also want to log the events of the turn
        #in an array of strings.
        self.current_turn = self.current_turn + 1
        turn_log = []

        #Loop through the Player List
        for p in self.players:
            #Log the players turn
            turn_log.append(f'{p.name}\'s turn begins.')

            #If player is bankrupt, skip turn
            if p.bankrupt:
                continue

            #Check if the player is in jail
            did_roll = False
            doubles_count = 0
            doubles = False
            roll = -1
            if p.in_jail:
                p.jail_turns = p.jail_turns + 1
                using_card = p.use_get_out_of_jail()
                will_pay = p.pay_out_of_jail()
                if using_card:
                    #Validate this move otherwise throw an exception
                    if p.get_out_of_jail > 0:
                        p.in_jail = False
                        p.jail_turns = 0
                        #Log this
                        turn_log.append(f'{p.name} uses a get out of jail free card.')
                    else:
                        raise AIException(f'AI-({p.name}) attempted to use get out of jail free card but did not have any!')
                elif will_pay:
                    #Validate this move
                    if p.money >= 50:
                        p.money = p.money - 50
                        p.in_jail = False
                        p.jail_turns = 0
                        #Log this
                        turn_log.append(f'{p.name} chooses to pay fine to leave jail.')
                    else:
                        raise AIException(f'AI-({p.name}) attempted to pay $50 jail fine but did only had ${p.money}!')
                else:
                    roll = p.roll_dice()
                    #Validate this result
                    self.validate_roll(p, roll)
                    #Log this
                    turn_log.append(f'{p.name} attempts to roll doubles to escape jail.')
                    turn_log.append(f'{p.name} rolled a {roll[0]} and a {roll[1]}.')
                    #Check we rolled doubles
                    if roll[0] == roll[1]:
                        did_roll = True
                        p.in_jail = False
                        p.jail_turns = 0
                        turn_log.append(f'{p.name} successfully rolled 2 {roll[0]}\'s to escape jail.')
            
            #Now check if player is still in jail to check turn limit
            if p.in_jail:
                #Check if jail turns is 3
                if p.jail_turns == 3:
                    #Check if they have enough money to pay fine
                    if p.money >= 50:
                        p.money = p.money - 50
                        p.in_jail = False
                        turn_log.append(f'{p.name} was forced to pay the fine to leave jail.')
                    else:
                        p.money = 0
                        p.bankrupt = True
                        turn_log.append(f'{p.name} could not afford to leave jail and has gone bankrupt.')
                else:
                    #Skip if not enough turns
                    turn_log.append(f'{p.name} is stuck in jail for this turn.')
                    continue
            
            #If we made it here, we are not in jail
            #Now we must perform a turn as long as doubles count is less than 3
            while doubles_count < 3 or did_roll:
                #If I did not roll, make a roll and validate it
                if not did_roll:
                    roll = p.roll_dice()
                    self.validate_roll(p, roll)
                    turn_log.append(f'{p.name} rolled a {roll[0]} and a {roll[1]}.')
                
                #Handle Doubles
                if roll[0] == roll[1] and not did_roll:
                    doubles_count = doubles_count + 1
                    doubles = True
                    turn_log.append(f'{p.name} has rolled doubles {doubles_count} times.')
                else:
                    doubles = False

                #Handle if the doubles count is 3
                if doubles_count == 3:
                    p.in_jail = True
                    p.jail_turns = 0
                    p.current_space = 10
                    turn_log.append(f'{p.name} has rolled doubles for the 3rd time sending them straight to jail.')

                #Now we must move the player an appropriate amount of spaces
                p.current_space = p.current_space + sum(roll)

                #Did we pass go?
                if p.current_space >= len(self.board):
                    p.money += 200
                    p.current_space = p.current_space % len(self.board)
                    turn_log.append(f'{p.name} passed Go and collected $200.')
                
                #We need to resolve where the player landed
                #For now we will print the space we land on
                space = self.board[p.current_space]
                if space == 'goto-jail':
                    p.current_space = 10
                    p.in_jail = True
                    p.jail_turns = 0
                    turn_log.append(f'{p.name} landed on Go To Jail, and is now in jail.')
                elif space == 'park':
                    turn_log.append(f'{p.name} landed on Free Parking.')
                    p.money += self.park_money
                    turn_log.append(f'{p.name} has claimed the ${self.park_money} that has accrued there.')
                    self.park_money = 0
                elif space == 'jail':
                    turn_log.append(f'{p.name} is Just Visiting Jail.')
                elif space == 'income-tax':
                    turn_log.append(f'{p.name} has landed on Income Tax')
                    if p.money < 200:
                        p.money = 0
                        p.bankrupt = True
                        turn_log.append(f'{p.name} could not afford Income Tax and has gone bankrupt.')
                    else:
                        p.money = p.money - 200
                        turn_log.append(f'{p.name} has paid $200 in Income Tax.')
                elif space == 'luxury-tax':
                    turn_log.append(f'{p.name} has landed on Luxury Tax')
                    if p.money < 200:
                        p.money = 0
                        p.bankrupt = True
                        turn_log.append(f'{p.name} could not afford Luxury Tax and has gone bankrupt.')
                    else:
                        p.money = p.money - 200
                        turn_log.append(f'{p.name} has paid $200 in Luxury Tax.')
                elif space == 'go':
                    turn_log.append(f'{p.name} has landed on Go.')
                elif isinstance(space, Chance):
                    turn_log.append(f'{p.name} has landed on Chance.')
                    #Now we need to draw a card and resolve it
                    card = space.draw()
                elif isinstance(space, CommunityChest):
                    turn_log.append(f'{p.name} has landed on Community Chest')
                else:
                    turn_log.append(f'{p.name} has landed on {space.name}')
                
                #Handle the possibility of the player going bankrupt.


                #Handle if we did roll from jail or we did not roll doubles
                if did_roll or not doubles:
                    break
            
            #Otherwise we are done with this player
        #For testing we want to print the turn log
        for message in turn_log:
            print(message)

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
        self.owner: BasePlayer = None
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
    
    def __str__(self) -> str:
        return 'Community Chest'

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
    
    def __str__(self) -> str:
        return 'Chance'

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
    def __init__(self, l: list[BasePlayer]) -> None:
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
    
    def __getitem__(self, k: int | str) -> BasePlayer:
        result = None
        if isinstance(k, int):
            result = self.l[k]
        elif isinstance(k,str):
            result = self.name_to_player.get(k)
        if result is None:
            raise KeyError(f'Invalid Key: {k}')
        return result

p1 = BasePlayer('Stephen')
p2 = BasePlayer('Sara')
p3 = BasePlayer('Jacob')
p4 = BasePlayer('Emily')
pl = PlayerList([p1,p2,p3,p4])

m = MonopolyBoard(pl)
m.turn()
m.turn()
m.turn()
m.turn()
m.turn()
m.turn()
m.turn()
m.turn()