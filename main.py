from Monopoly import MonopolyBoard, PlayerList, BasePlayer, AI_Stephen

bots = PlayerList([AI_Stephen('Bot One'),AI_Stephen('Bot Two'),AI_Stephen('Bot Three'),AI_Stephen('Bot Four')])
m = MonopolyBoard(bots)

game_count = 10000
turn_max = 200

terminate_count = 0
space_distribution_overall = [0]*40
space_distribution_per_player = [[0]*40,[0]*40,[0]*40,[0]*40]
space_distribution_winners = [0]*40
space_distribution_bankrupts = [0]*40

m.simulate_game()