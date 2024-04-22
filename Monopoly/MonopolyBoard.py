from __future__ import annotations
import path
import csv
from random import shuffle, randint
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
        self.player_space_distributions = {}
        for p in self.players:
            self.player_space_distributions[p] = [0]*40

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

    def simulate_turns(self, n: int, show_turn_log = False):
        for _ in range(n):
            self.turn(show_turn_log)
    
    def reset(self):
        for p in self.players:
            p.reset()
        self.current_turn = 0
        for s in self.board:
            if isinstance(s, Property) or isinstance(s, RailRoad) or isinstance(s, Utility):
                s.reset()
        shuffle(self.players)

    def resolve_jail(self, p: BasePlayer, turn_log: list[str]) -> tuple[int, int]:
        """This is called when a player starts their turn in jail.

        Args:
            p (_type_): Player to resolve turn for.
        """
        #Increment number of turns spent in jail
        p.jail_turns = p.jail_turns + 1

        #Query whether or not the player will use a get out of jail free card.
        using_card = p.use_get_out_of_jail()

        #Query whether or not the player will pay to get out of jail.
        will_pay = p.pay_out_of_jail()

        #Using a get out of jail free card takes priority
        if using_card:
            if p.get_out_of_jail < 1:
                raise AIException(f'{p.name} attempted to use a nonexistent Get Out of Jail Free card!')
            p.get_out_of_jail -= 1
            p.in_jail = False
            p.jail_turns = 0
            turn_log.append(f'{p.name} chose to use a Get Out of Jail Free card.')
            return None
        elif will_pay:
            #Check if player has enough in liquidity to afford
            if p.liquidity < 50:
                raise AIException(f'{p.name} tried to pay the $50 but did not have enough liquid.')
            #Now ensure the player liquidates enough to have cash on hand.
            if p.liquidate(50, turn_log):
                #Player has enough in cash and we can pay
                p.money = p.money - 50
                p.liquidity -= 50
                self.park_money += 50
                p.in_jail = False
                p.jail_turns = 0
                turn_log.append(f'{p.name} chose to pay $50 to get out of jail.')
                return None
            else:
                #The player chose not to liquidate and thus is bankrupt, so perform bankruptcy protocol
                self.resolve_bankruptcy(p, None, turn_log)
        else:
            #Player must roll dice to escape
            roll = p.roll_dice(turn_log)
            self.validate_roll(p, roll)
            #Now check if it was doubles
            if roll[0] == roll[1]:
                p.in_jail = False
                p.jail_turns = 0
                turn_log.append(f'{p.name} rolled doubles allowing them to leave jail.')
                return roll
            else:
                #Check if it was the third turn
                if p.jail_turns == 3:
                    #Check if the player has enough in liquidity
                    if p.liquidity < 50:
                        #Now the player is bankrupt
                        p.bankrupt = True
                        turn_log.append(f'{p.name} could not afford the $50 fine and is now bankrupt.')
                        return None
                    #Let the player liquidate
                    if p.liquidate(50, turn_log):
                        #Player has enough cash to pay
                        p.money = p.money - 50
                        p.liquidity -= 50
                        self.park_money += 50
                        p.in_jail = False
                        p.jail_turns = 0
                        turn_log.append(f'{p.name} was forced to pay the $50 fine to leave jail.')
                        return None
                    else:
                        self.resolve_bankruptcy(p, None, turn_log)
                        return None
                else:
                    #They have more turns to spend in jail
                    return None

    def auction_property(self, property: Property | RailRoad | Utility, turn_log: list[str]):
        current_bid = 0
        current_player = None
        turn_log.append(f'Auction Beginning for {property.name}.')
        for p in self.players:
            #Skip if this player is out of the game
            if p.bankrupt or current_player is p:
                continue
            
            #Query the player for his or her bid
            competing_offer = p.make_auction_offer(property, 0)
            #Validate this offer with the players liquidity
            if competing_offer > p.liquidity:
                raise AIException(f'{p.name} attempted to bid ${competing_offer} when they only have ${p.liquidity} in liquidity.')

            #If it is larger than the current offer, then it stands
            if competing_offer > current_bid:
                current_bid = competing_offer
                current_player = p
                turn_log.append(f'{current_player.name} raised the offer to ${current_bid}.')
        
        #Now that we've settled on a price, sell it to the player
        if current_bid == 0:
            turn_log.append(f'No one participated in the auction. The property remains undeveloped.')
        else:
            if current_player.liquidate(current_bid, turn_log):
                #Take the money from the player and make them the owner of the property
                current_player.money -= current_bid
                current_player.liquidity -= current_bid
                
                #Since this is a purchase, we clean the slate for the property
                property.reset()
                self.acquire_property(property, current_player)
                turn_log.append(f'{current_player.name} won the auction for {property.name}.')
            else:
                #Player won the bid but chose to go bankrupt? This should not happen
                raise AIException(f'{current_player.name} won the auction but did not liquidate enough capital? Are you stupid?')

    def update_monopolies(self):
        for color in set([prop.color for prop in self.board if isinstance(prop, Property)]):
            if len(set([prop.owner for prop in self.board if isinstance(prop, Property) and prop.color == color])) == 1:
                for prop in self.board:
                    if isinstance(prop, Property) and prop.color == color:
                        prop.is_monopoly = True

    def acquire_property(self, property: Property | RailRoad | Utility, p: BasePlayer):
        # if not property.owner is None:
        #     if isinstance(property, Property):
        #         property.owner.properties.remove(property)
        #     elif isinstance(property, RailRoad):
        #         property.owner.railroads.remove(property)
        #     else:
        #         property.owner.utilities.remove(property)
        property.owner = p
        if isinstance(property, Property):
            p.properties.add(property)
        elif isinstance(property, RailRoad):
            p.railroads.add(property)
        else:
            p.utilities.add(property)
        p.liquidity += property.mortgage_value
        if isinstance(property, Property):
            p.liquidity += property.house_cost*property.house_count + property.hotel_cost*property.hotel_count
        self.update_monopolies()

    def resolve_space(self, space, p: BasePlayer, turn_log: list[str]):
        if space == 'go':
            #Nothing happens.
            turn_log.append(f'{p.name} landed on Go.')
        elif space == 'jail':
            #Player is just visiting
            turn_log.append(f'{p.name} is just visiting jail.')
        elif space == 'park':
            #Have the player claim money if there is any
            turn_log.append(f'{p.name} landed on Free Parking.')
            if self.park_money > 0:
                p.money = p.money + self.park_money
                p.liquidity = p.liquidity + self.park_money
                turn_log.append(f'{p.name} collected ${self.park_money} from Free Parking.')
                self.park_money = 0
        elif space == 'goto-jail':
            #Send this player to jail
            p.in_jail = True
            p.jail_turns = 0
            p.current_space = 10
            rolled_doubles = False
            turn_log.append(f'{p.name} landed on Go To Jail and has been sent straight to jail.')
        elif space == 'income-tax':
            #Handle a possible transaction
            turn_log.append(f'{p.name} landed on Income Tax.')
            #Check liquidity
            if p.liquidity < 200:
                #Player is now bankrupt
                turn_log.append(f'{p.name} could not afford the tax and is now bankrupt.')
                self.resolve_bankruptcy(p, None, turn_log)
            #Otherwise let the player liquidate
            if p.liquidate(200, turn_log):
                #They now have enough money
                p.money -= 200
                p.liquidity -= 200
                self.park_money += 200
                turn_log.append(f'{p.name} paid the $200 Income Tax.')
            else:
                #Player did not liquidate and is bankrupt
                turn_log.append(f'{p.name} chose not to liquidate assets and is now bankrupt.')
                self.resolve_bankruptcy(p, None, turn_log)
        elif space == 'luxury-tax':
            #Handle a possible transaction
            turn_log.append(f'{p.name} landed on Luxury Tax.')
            #Check liquidity
            if p.liquidity < 200:
                #Player is now bankrupt
                p.bankrupt = True
                turn_log.append(f'{p.name} could not afford the tax and is now bankrupt.')
                self.resolve_bankruptcy(p, None, turn_log)
            #Otherwise let the player liquidate
            if p.liquidate(200, turn_log):
                #They now have enough money
                p.money -= 200
                p.liquidity -= 200
                self.park_money += 200
                turn_log.append(f'{p.name} paid the $200 Luxury Tax.')
            else:
                #Player did not liquidate and is bankrupt
                p.bankrupt = True
                turn_log.append(f'{p.name} chose not to liquidate assets and is now bankrupt.')
                self.resolve_bankruptcy(p, None, turn_log)
        elif isinstance(space, CommunityChest):
            #For now we will just print the name of the space
            turn_log.append(f'{p.name} landed on Community Chest.')

            #Draw the card
            card = space.draw()
            turn_log.append(f'{card}')

            #Handle the payee
            if card.payee == 'self':
                if not card.payer == 'all':
                    p.money += card.amount
                    p.liquidity += card.amount
            elif card.payee == 'park':
                tmp_amount = 0
                #Check if card amount is -1
                if card.amount == -1:
                    #We need to look over all of p's properties and count up a total
                    for prop in p.properties:
                        tmp_amount += 40*prop.house_count + 115*prop.hotel_count
                else:
                    tmp_amount = card.amount
                #Check if player has enough liquid
                if p.liquidity < tmp_amount:
                    p.bankrupt
                    turn_log.append(f'{p.name} could not afford the ${tmp_amount} and is now bankrupt.')
                    self.resolve_bankruptcy(p, None, turn_log)
                elif p.liquidate(tmp_amount, turn_log):
                    #Player has enough cash
                    p.money -= tmp_amount
                    p.liquidity -= tmp_amount
                    self.park_money += tmp_amount
                else:
                    p.bankrupt
                    turn_log.append(f'{p.name} chose not to liquidate and is now bankrupt.')
                    self.resolve_bankruptcy(p, None, turn_log)
            
            #Handle the payer being all
            if card.payer == 'all':
                #Now we need to loop over all players that are not p and transact
                total = 0
                for o in self.players:
                    if o is p or o.bankrupt:
                        continue
                    if o.liquidity < card.amount:
                        o.bankrupt = True
                        turn_log.append(f'{o.name} could not afford to pay ${card.amount} to {p.name} and is now bankrupt.')
                        self.resolve_bankruptcy(o, None, turn_log)
                    elif o.liquidate(card.amount, turn_log):
                        o.money -= card.amount
                        o.liquidity -= card.amount
                        total += card.amount
                        turn_log.append(f'{o.name} paid {p.name} ${card.amount}.')
                    else:
                        o.bankrupt = True
                        turn_log.append(f'{o.name} chose not to liquidate and is now bankrupt.')
                        self.resolve_bankruptcy(o, None, turn_log)
                p.money += total
                p.liquidity += total
            
            #Handle the go to
            if card.goto == 'go':
                p.money += 200
                p.liquidity += 200
                turn_log.append(f'{p.name} has passed Go and collected $200')
                p.current_space = 0
                turn_log.append(f'{p.name} landed on Go.')
                self.player_space_distributions[p][0] += 1
            elif card.goto == 'jail':
                p.current_space = 10
                p.in_jail = True
                p.jail_turns = 0
                turn_log.append(f'{p.name} landed in Jail.')
                self.player_space_distributions[p][10] += 1
            
            #Handle the get out of jail free card
            if card.payer is None and card.payee is None and card.goto is None:
                p.get_out_of_jail += 1
                    
        elif isinstance(space, Chance):
            #For now we will just print the name of the space
            turn_log.append(f'{p.name} landed on Chance.')

            #Draw a card
            card = space.draw()
            turn_log.append(f'{card}')

            #Resolve the card
            if card.payee == 'none' and card.payer == 'none':
                #Check for get out of jail free
                if card.goto == 'none':
                    if card.amount == 0:
                        p.get_out_of_jail += 1
                    else:
                        p.current_space = (p.current_space - 3) % 40
                        self.resolve_space(self.board[p.current_space], p, turn_log)
                else:
                    if card.goto == 'go':
                        p.current_space = 0
                        self.player_space_distributions[p][p.current_space] += 1
                        turn_log.append(f'{p.name} passed Go and collected $200.')
                    elif card.goto == 'jail':
                        p.current_space = 10
                        p.in_jail = True
                        p.jail_turns = 3
                        self.player_space_distributions[p][p.current_space] += 1
                        turn_log.append(f'{p.name} was sent to jail.')
                    elif card.goto == 'utility':
                        passed_go = False
                        if p.current_space < 12:
                            p.current_space = 12
                        elif p.current_space < 28:
                            p.current_space = 28
                        else:
                            p.current_space = 12
                            passed_go = True
                        if passed_go:
                            p.money += 200
                            p.liquidity += 200
                            turn_log.append(f'{p.name} passed Go and collected $200')
                        self.player_space_distributions[p][p.current_space] += 1
                        self.resolve_space(self.board[p.current_space], p, turn_log)
                    elif card.goto == 'railroad':
                        passed_go = False
                        if p.current_space < 5:
                            p.current_space = 5
                        elif p.current_space < 15:
                            p.current_space = 15
                        elif p.current_space < 25:
                            p.current_space = 25
                        elif p.current_space < 35:
                            p.current_space = 35
                        else:
                            p.current_space = 5
                            passed_go = True
                        if passed_go:
                            p.money += 200
                            p.liquidity += 200
                            turn_log.append(f'{p.name} passed Go and collected $200.')
                        self.player_space_distributions[p][p.current_space] += 1
                        self.resolve_space(self.board[p.current_space], p, turn_log)
                    elif card.goto == 'Illinois Avenue':
                        if p.current_space >= 23:
                            p.money += 200
                            p.liquidity += 200
                            turn_log.append(f'{p.name} passed Go and collected $200.')
                        p.current_space = 23
                        self.player_space_distributions[p][p.current_space] += 1
                        self.resolve_space(self.board[p.current_space], p, turn_log)
                    elif card.goto == 'St. Charles Place':
                        if p.current_space >= 11:
                            p.money += 200
                            p.liquidity += 200
                            turn_log.append(f'{p.name} passed Go and collected $200.')
                        p.current_space = 11
                        self.player_space_distributions[p][p.current_space] += 1
                        self.resolve_space(self.board[p.current_space], p, turn_log)
                    elif card.goto == 'Reading Railroad':
                        if p.current_space >= 5:
                            p.money += 200
                            p.liquidity += 200
                            turn_log.append(f'{p.name} passed Go and collected $200.')
                        p.current_space = 5
                        self.player_space_distributions[p][p.current_space] += 1
                        self.resolve_space(self.board[p.current_space], p, turn_log)
                    elif card.goto == 'Boardwalk':
                        if p.current_space >= 39:
                            p.money += 200
                            p.liquidity += 200
                            turn_log.append(f'{p.name} passed Go and collected $200.')
                        p.current_space = 39
                        self.player_space_distributions[p][p.current_space] += 1
                        self.resolve_space(self.board[p.current_space], p, turn_log)
            else:
                if card.payee == 'self':
                    p.money += card.amount
                    p.liquidity += card.amount
                elif card.payee == 'park':
                    #This means it is coming from the player, so calculate the amount
                    tmp_amount = card.amount
                    if card.amount == -2:
                        tmp_amount = 0
                        for prop in p.properties:
                            tmp_amount += 25*prop.house_count + 100*prop.hotel_count
                    if p.liquidity < tmp_amount:
                        p.bankrupt = True
                        turn_log.append(f'{p.name} could not afford to pay ${tmp_amount} and has gone bankrupt.')
                        self.resolve_bankruptcy(p, None, turn_log)
                        #Handle bankruptcy
                    else:
                        if p.liquidate(tmp_amount, turn_log):
                            p.money -= tmp_amount
                            p.liquidity -= tmp_amount
                            turn_log.append(f'{p.name} has liqidated and payed ${tmp_amount}.')
                        else:
                            p.bankrupt = True
                            turn_log.append(f'{p.name} chose not to liquidate and has gone bankrupt.')
                            self.resolve_bankruptcy(p, None, turn_log)
                            #Handle Bankruptcy
                elif card.payee == 'all':
                    tmp_amount = 50*(len([o for o in self.players if not o.bankrupt])-1)
                    if p.liquidity < tmp_amount:
                        p.bankrupt = True
                        turn_log.append(f'{p.name} could not afford to pay ${tmp_amount} and has gone bankrupt.')
                        self.resolve_bankruptcy(p, None, turn_log)
                        #Handle bankruptcy
                    else:
                        if p.liquidate(tmp_amount, turn_log):
                            p.money -= tmp_amount
                            p.liquidity -= tmp_amount
                            for ply in self.players:
                                if not ply is p and not ply.bankrupt:
                                    ply.money += 50
                                    ply.liquidity += 50
                            turn_log.append(f'{p.name} payed all players $50.')
                        else:
                            p.bankrupt = True
                            turn_log.append(f'{p.name} chose not to liquidate and has gone bankrupt.')
                            self.resolve_bankruptcy(p, None, turn_log)
        elif isinstance(space, Utility) or isinstance(space, Property) or isinstance(space, RailRoad):
            turn_log.append(f'{p.name} landed on {space.name}.')
            if space.owner is None:
                if not self.purchase_property(space, p, turn_log):
                    self.auction_property(space, turn_log)
            elif not space.owner is p:
                rent = space.rent()
                if p.liquidity < rent:
                    self.resolve_bankruptcy(p, space.owner, turn_log)
                else:
                    if p.liquidate(rent, turn_log):
                        p.money -= rent
                        p.liquidity -= rent
                        space.owner.money += rent
                        space.owner.liquidity += rent
                        turn_log.append(f'{p.name} payed ${rent} to {space.owner.name} for rent.')
                    else:
                        self.resolve_bankruptcy(p, space.owner, turn_log)

    def resolve_bankruptcy(self, p: BasePlayer, o: BasePlayer | None, turn_log: list[str]):
        p.bankrupt = True
        if not o is None:
            #Owes a player
            o.money += p.money
            o.liquidity += p.money
            for prop in p.properties:
                self.acquire_property(prop, o)
            for rr in p.railroads:
                self.acquire_property(rr, o)
            for ut in p.utilities:
                self.acquire_property(ut, o)
            p.properties = set()
            p.railroads = set()
            p.utilities = set()
            o.get_out_of_jail += p.get_out_of_jail
            p.get_out_of_jail = 0
            p.money = 0
            p.liquidity = 0
            turn_log.append(f'{p.name} has given {o.name} all money and assets.')
        else:
            #Owes the bank, player loses all money and liquidity
            #Auctions all properties, railroads, and utilities to the rest of the players
            p.money = 0
            p.liquidity = 0
            for prop in p.properties:
                self.auction_property(prop, turn_log)
            for rr in p.railroads:
                self.auction_property(rr, turn_log)
            for ut in p.utilities:
                self.auction_property(ut, turn_log)

    def purchase_property(self, property: Property | RailRoad | Utility, p: BasePlayer, turn_log: list[str]) -> bool:
        if p.should_buy_property(property):
            if p.liquidate(property.price, turn_log):
                p.money -= property.price
                p.liquidity -= property.price
                property.reset()
                self.acquire_property(property, p)
                turn_log.append(f'{p.name} purchased {property.name} for ${property.price}.')
                return True
            else:
                raise AIException(f'{p.name} wanted to buy a property, but refused to liquidate in order to afford it.')
        return False

    def turn(self, show_turn_log = False):
        #Check if we have already ended the game
        if len([p for p in self.players if not p.bankrupt]) == 1:
            return
        #First we increment the number of turns performed, we also want to log the events of the turn
        #in an array of strings.
        self.current_turn = self.current_turn + 1
        turn_log = []

        #Loop through the Player List
        for p in self.players:
            #If player is bankrupt, skip turn
            if p.bankrupt:
                continue

            #Log the players turn
            turn_log.append(f'{p.name}\'s turn begins.')

            #Check if the player is in jail
            jail_roll = None
            if p.in_jail:
                jail_roll = self.resolve_jail(p, turn_log)
            
            #Check if player is bankrupt for good measure or still in jail
            if p.bankrupt or p.in_jail:
                continue

            #Now we need to perform turns until we hit a stopping condition
            doubles_count = 0
            rolled_doubles = False
            while True:
                #If we have a valid jail roll, use that otherwise make a roll
                roll = jail_roll
                if roll is None:
                    roll = p.roll_dice(turn_log)
                    self.validate_roll(p, roll)
                
                #Now check if we rolled doubles and increment, but only if it was not a jail roll
                if jail_roll is None and roll[0] == roll[1]:
                    doubles_count += 1
                    turn_log.append(f'{p.name} has rolled doubles {doubles_count} time(s).')
                    #Check if doubles count is 3, if so send straight to jail and resolve rolling
                    if doubles_count == 3:
                        p.in_jail = True
                        p.jail_turns = 0
                        p.current_space = 10
                        turn_log.append(f'{p.name} has been straight to jail.')
                        break
                    else:
                        rolled_doubles = True
                else:
                    rolled_doubles = False
                
                #Now we move the player
                p.current_space = p.current_space + sum(roll)
                if p.current_space >= 40:
                    p.money += 200
                    p.liquidity += 200
                    p.current_space = p.current_space % 40
                    turn_log.append(f'{p.name} passed Go and collected $200.')

                #We now resolve the space the player has landed on. We will process them in order of complexity
                space = self.board[p.current_space]
                self.player_space_distributions[p][p.current_space] += 1
                self.resolve_space(space, p, turn_log)
                
                #Check if we end the turn here
                if not jail_roll is None or not rolled_doubles or p.bankrupt:
                    break
            
            #Now we loop over the properties owned buy this player that are monopolies and ask if they would like to buy a house
            did_buy = True
            while did_buy:
                did_buy = False
                for prop in p.properties:
                    if prop.is_monopoly and prop.house_count < 4 and prop.hotel_count < 1 and all([o.house_count >= prop.house_count for o in p.properties if not o is prop and o.color == prop.color]):
                        if p.liquidity > prop.house_cost and p.should_buy_house(prop):
                            if p.liquidate(prop.house_cost, turn_log):
                                p.money -= prop.house_cost
                                p.liquidity -= prop.house_cost
                                prop.house_count += 1
                                p.liquidity += prop.house_cost // 2
                                turn_log.append(f'{p.name} bought a house on {prop.name}. It now has {prop.house_count} house(s).')
                                did_buy = True
            
            #Now we loop over the properties owned to offer hotel purchases
            did_buy = True
            while did_buy:
                did_buy = False
                for prop in p.properties:
                    if prop.house_count == 4 and p.should_buy_hotel(prop):
                        if p.liquidate(prop.hotel_cost, turn_log):
                            p.money -= prop.hotel_cost
                            p.liquidity -= prop.hotel_cost
                            prop.house_count = 0
                            prop.hotel_count = 1
                            p.liquidity -= 4 * (prop.house_cost // 2)
                            p.liquidity += prop.hotel_cost // 2
                            turn_log.append(f'{p.name} has purchased a hotel for {prop.name}.')
                            did_buy = True

            #Otherwise we are done with this player
        if show_turn_log:
            for message in turn_log:
                print(message)
            for p in self.players:
                print(f'{p.name: <10}: Money ${p.money} vs ${p.liquidity} Liquidity.')
        
        self.game_log[self.current_turn] = turn_log

    def __str__(self) -> str:
        s = f'Turns Passes: {self.current_turn}\n'
        for p in self.players:
            s += f'{p.name: <10} - Cash = ${p.money:<5} Net Worth = ${p.liquidity}\n'
        return s

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
        self.owner: BasePlayer = None
        self.house_count = 0
        self.hotel_count = 0
        self.is_mortgaged = False
        self.is_monopoly = False

    def reset(self):
        self.owner = None
        self.house_count = 0
        self.hotel_count = 0
        self.is_mortgaged = False
        self.is_monopoly = False
    
    def rent(self) -> int:
        if self.hotel_count == 1:
            return self.rents[5]
        elif self.house_count > 0:
            return self.rents[self.house_count]
        elif self.is_monopoly:
            return 2 * self.rents[0]
        return self.rents[0]

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
    
    def reset(self):
        self.owner: BasePlayer = None
        self.is_mortgaged = False
        self.amount_owned = 0
    
    def rent(self):
        return self.rents[self.amount_owned]

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
    
    def reset(self):
        self.owner = None
        self.is_mortgaged = False
        self.amount_owned = 0
    
    def rent(self):
        return self.rents[self.amount_owned] * (randint(1,6) + randint(1,6))

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
    
    def __setitem__(self, k: int, p: BasePlayer) -> None:
        self.l[k] = p

p1 = BasePlayer('Stephen')
p2 = BasePlayer('Sara')
p3 = BasePlayer('Jacob')
p4 = BasePlayer('Emily')
pl = PlayerList([p1,p2,p3,p4])

turn_counts = []
p1_scores = []
p2_scores = []
p3_scores = []
p4_scores = []

game_number = 1000
turn_max = 100
m = MonopolyBoard(pl)
for _ in range(game_number):
    m.reset()
    m.simulate_turns(turn_max, False)
    turn_counts.append(m.current_turn)
    p1_scores.append(p1.liquidity / m.current_turn)
    p2_scores.append(p2.liquidity / m.current_turn)
    p3_scores.append(p3.liquidity / m.current_turn)
    p4_scores.append(p4.liquidity / m.current_turn)

nt = [t for t in turn_counts if t < turn_max]
if len(nt) > 0:
    print(f'Average Game Length of a Terminated Game: {sum(nt) / len(nt)} (Occurs {(100*len(nt)/len(turn_counts)):0.2f}% of the time.)')
print(f'Average Score: {(sum(p1_scores) + sum(p2_scores) + sum(p3_scores) + sum(p4_scores)) / (len(p1_scores) + len(p2_scores) + len(p3_scores) + len(p4_scores))}')
print(f'Stephen Average: {sum(p1_scores) / len(p1_scores)}')
print(f'Stephen Distribution: {m.player_space_distributions[p1]}')
print(f'Sara Average: {sum(p2_scores) / len(p2_scores)}')
print(f'Sara Distribution: {m.player_space_distributions[p2]}')
print(f'Jacob Average: {sum(p3_scores) / len(p3_scores)}')
print(f'Jacob Distribution: {m.player_space_distributions[p3]}')
print(f'Emily Average: {sum(p4_scores) / len(p4_scores)}')
print(f'Emily Distribution: {m.player_space_distributions[p4]}')