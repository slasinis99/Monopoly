from Monopoly import MonopolyBoard, PlayerList, BasePlayer, AI_Jillian, Chance, CommunityChest, AI_George
from statistics import mean, stdev
import numpy as np

def generate_stats(m: MonopolyBoard, game_count: int = 10_000, turn_limit: int = 200) -> None:
    terminate_count = 0
    terminate_turns = []
    space_distribution_overall = [0]*40
    space_distribution_per_player = {}
    scores = {}
    for p in m.players:
        space_distribution_per_player[p] = [0]*40
        scores[p] = 0
    space_distribution_winners = [0]*40
    space_distribution_bankrupts = [0]*40

    for _ in range(game_count):
        m.simulate_game(turn_limit, show_turn_log=False)

        #Gather the Statistics
        if m.current_turn < turn_limit:
            terminate_count += 1
            terminate_turns.append(m.current_turn)
        
        #Handle the overall space distribution
        for p in m.players:
            scores[p] += (p.money + 2*(p.liquidity-p.money)) / m.current_turn
            for i in range(40):
                space_distribution_overall[i] += m.player_space_distributions[p][i]
                space_distribution_per_player[p][i] += m.player_space_distributions[p][i]
            if p.money == 0:
                for i in range(40):
                    space_distribution_bankrupts[i] += m.player_space_distributions[p][i]
        
        #Handle Exactly One Winner
        if len([p for p in m.players if p.money > 0]) == 1:
            for p in m.players:
                if p.money > 0:
                    for i in range(40):
                        space_distribution_winners[i] += m.player_space_distributions[p][i]
    
    #Now present all findings
    print(f'Exactly {terminate_count} games out of {game_count} actually terminated. ({terminate_count / game_count})\n')
    print(f'Mean turn count for terminated games: {mean(terminate_turns)}, Standard Deviation: {stdev(terminate_turns)}')

    #Now we need to turn distributions into percentages
    overall_s = sum(space_distribution_overall)
    overall_per = {}
    for p in m.players:
        overall_per[p] = sum(space_distribution_per_player[p])
    overall_win = sum(space_distribution_winners)
    overall_bankrupt = sum(space_distribution_bankrupts)
    for i in range(40):
        space_distribution_overall[i] = space_distribution_overall[i] / overall_s
        space_distribution_bankrupts[i] = space_distribution_bankrupts[i] / overall_bankrupt
        space_distribution_winners[i] = space_distribution_winners[i] / overall_win
        for p in m.players:
            space_distribution_per_player[p][i] = space_distribution_per_player[p][i] / overall_per[p]
    
    #Now we z-score the overall distribution
    z_score = [(v - mean(space_distribution_overall)) / stdev(space_distribution_overall) for v in space_distribution_overall]

    M = create_transition_matrix()
    v = create_initial_vector()
    b = (M**1000)*v

    s = f'{" "*25}{"Z-Score": ^10}{"Overall": ^10}{"Markov": ^10}{"Winners": ^10}{"Bankrupt": ^10}\n'
    for i in range(40):
        sp = m.board[i]
        if isinstance(sp, str) or isinstance(sp, Chance) or isinstance(sp, CommunityChest):
            s += f'{str(sp): <25}'
        else:
            s += f'{sp.name: <25}'
        s += f'{f"{z_score[i]:0.2f}": ^10}{f"{100*space_distribution_overall[i]:0.2f}%": ^10}{f"{float(100*b[i]):0.2f}%": ^10}{f"{100*space_distribution_winners[i]:0.2f}%": ^10}{f"{100*space_distribution_bankrupts[i]:0.2f}%": ^10}'
        s += f'\n'
    print(s)

    s = f'\nAverage Scores\n'
    for p in m.players:
        s += f'{p.name: <10}: {scores[p]/game_count}\n'
    print(s)

def create_transition_matrix():
    P = [0,0,1,2,3,4,5,6,5,4,3,2,1]
    M = [40*[0] for _ in range(40)]
    for i in range(40):
        if i == 30:
            M[10][i] = 1
            continue
        M[10][i] += (6/36)**3
        for j in range(2, 13):
            v = (i+j) % 40
            p = (1 - (6/36)**3) * P[j] / 36
            if v in [2,17,33]:
                M[v][i] += p*15/17
                M[0][i] += p*1/17
                M[10][i] += p*1/17
            elif v in [7,22,36]:
                M[v][i] += p*6/16
                M[0][i] += p*1/16
                M[5][i] += p*1/16
                M[24][i] += p*1/16
                M[11][i] += p*1/16
                M[39][i] += p*1/16
                M[v-3][i] += p*1/16
                M[10][i] += p*1/16
                if v == 7:
                    M[12][i] += p*1/16
                    M[15][i] += p*2/16
                elif v == 22:
                    M[28][i] += p*1/16
                    M[25][i] += p*2/16
                else:
                    M[12][i] += p*1/16
                    M[5][i] += p*2/16
            else:
                M[v][i] += p
    return np.matrix(M)

def create_initial_vector():
    v = 40*[0]
    v[0] = 1
    return np.transpose(np.matrix(v))

b = [BasePlayer('Bot One'), BasePlayer('Bot Two'), BasePlayer('Bot Three'), BasePlayer('Bot Four')]
jill = [AI_Jillian('Jillian One'), AI_Jillian('Jillian Two'), AI_Jillian('Jillian Three'), AI_Jillian('Jillian Four')]
george = [AI_George('George One'), AI_George('George Two'), AI_George('George Three'), AI_George('George Four')]

m = MonopolyBoard(PlayerList([b[0], b[1], b[2], b[3]]))

generate_stats(m, 1_000, 1_000)