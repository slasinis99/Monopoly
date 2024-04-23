from Monopoly import MonopolyBoard, BasePlayer, AI_Stephen, PlayerList

#Create the AI Players we wish to use
AI_ONE = AI_Stephen('Stephen')
AI_TWO = AI_Stephen('Bot Two')
AI_THREE = BasePlayer('Bot Three')
AI_FOUR = BasePlayer('Bot Four')

#Compile them into a player list
player_list = PlayerList([AI_ONE, AI_TWO])

#Create the Monopoly Board
mb = MonopolyBoard(player_list)

#Now we can simulate a game
mb.simulate_game(max_turns=100, show_turn_log=True)