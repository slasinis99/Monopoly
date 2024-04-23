from random import randint

class BasePlayer():
    """A base class to represent a player in Monopoly. Any subclasses must be sure to properly implement
    or inherit the following methods:

    roll_dice(self, turn_log: list[str]) -> tuple[int, int]

    should_buy_property(self, property) -> bool

    make_auction_offer(self,property) -> int

    use_get_out_of_jail(self) -> bool

    pay_out_of_jail(self) -> bool

    liquidate(self, amount: int, turn_log: list[str])

    should_buy_house(self, property) -> bool

    should_buy_hotel(self, property) -> bool

    buy_back_mortgage(self, property) -> bool
    """
    def __init__(self, name) -> None:
        #Immutable Fields
        self.name = name

        #Mutable Fields
        self.bankrupt = False
        self.money = 1500
        self.liquidity = 1500
        self.current_space = 0
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail = 0
        self.properties = set()
        self.railroads = set()
        self.utilities = set()

    def reset(self):
        self.bankrupt = False
        self.money = 1500
        self.liquidity = 1500
        self.current_space = 0
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail = 0
        self.properties = set()
        self.railroads = set()
        self.utilities = set()

    def roll_dice(self, turn_log: list[str]) -> tuple[int, int]:
        """Roll 2d6 and return in a tuple.

        Returns:
            tuple[int, int]: Tuple containing both dice rolls.
        """
        roll = (randint(1,6), randint(1,6))
        turn_log.append(f'{self.name} rolled a {roll[0]} and a {roll[1]}')
        return roll
    
    def should_buy_property(self, property) -> bool:
        """Given a property: would you like to purchase it?

        Args:
            property (_type_): Property/Railroad/Utility

        Returns:
            bool: True/False depending on decision.
        """
        if self.money >= property.price:
            return True
        return False
    
    def make_auction_offer(self, property, current_offer) -> int:
        """Given a property and auction offer, choose an amount to counter with.

        Args:
            property (_type_): Property/Railroad/Utility in question.
            current_offer (_type_): The current winning bid.

        Returns:
            int: New amount to bid (larger than current offer). (0 for decline to bid.)
        """
        if self.money <= current_offer:
            return 0
        inc = current_offer + randint(1,10)
        if inc > self.money: inc = current_offer + 1
        if self.money > inc and inc <= property.price:
            return inc
        return 0
    
    def use_get_out_of_jail(self) -> bool:
        """Answers the question: would you like to use a get out of jail free card?

        Returns:
            bool: True/False depending on decision.
        """
        if self.get_out_of_jail > 0:
            return True
        return False
    
    def pay_out_of_jail(self) -> bool:
        """Answers the question: would you like to pay the fine to get out of jail?

        Returns:
            bool: True/False depending on decision.
        """
        if self.money >= 50:
            return True
        return False
    
    def liquidate(self, amount: int, turn_log: list[str]) -> bool:
        """The player must liquidate assets in order to have the required amount in cash (i.e., self.money)

        Args:
            amount (int): The amount required minimum in order to be liquid.

        Returns:
            bool: True if we successfully liquidated, False if we decided not (i.e., chose bankruptcy)
        """
        #Base Implementation will not liquidate any assets.
        if self.money < amount:
            return False
        else:
            return True
    
    def should_buy_house(self, property) -> bool:
        """Given a property that I am allowed to buy a house for, do I?

        Args:
            property (_type_): The property object, fields found in other file.

        Returns:
            bool: True/False that I want to buy.
        """
        if self.money > 3*property.house_cost:
            return True
        return False
    
    def should_buy_hotel(self, property) -> bool:
        """Given a property that I am allowed to buy a hotel for, do I?

        Args:
            property (_type_): The property object, fields found in other file.

        Returns:
            bool: True/False that I want to buy.
        """
        if self.money > 2*property.hotel_cost:
            return True
        return False
    
    def buy_back_mortgage(self, property) -> bool:
        if self.money >= property.mortgage_value:
            return True