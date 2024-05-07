import matplotlib.pyplot as plt

dpd = [0.03057861328125, 0.0213470458984375, 0.01898193359375, 0.021636962890625, 0.0232391357421875, 0.0296173095703125, 0.0225372314453125, 0.008636474609375, 0.02313232421875, 0.0229644775390625, 0.062744140625, 0.0269927978515625, 0.0260009765625, 0.023712158203125, 0.024627685546875, 0.0291748046875, 0.027923583984375, 0.0261688232421875, 0.02935791015625, 0.0308380126953125, 0.028839111328125, 0.0283660888671875, 0.0104827880859375, 0.0273284912109375, 0.031829833984375, 0.0306549072265625, 0.027069091796875, 0.026763916015625, 0.028045654296875, 0.0258331298828125, 0.0, 0.0267486572265625, 0.026214599609375, 0.0240020751953125, 0.02496337890625, 0.0243072509765625, 0.00865936279296875, 0.021881103515625, 0.02178955078125, 0.0262908935546875]

colors = ['Brown', 'Light Blue', 'Pink', 'Orange', 'Red', 'Yellow', 'Green', 'Dark Blue']
color_map = {'Brown':[1,3], 'Light Blue':[6,8,9], 'Pink':[11,13,14], 'Orange':[16,18,19], 'Red':[21,23,24], 'Yellow':[26,28,29], 'Green':[31,32,34], 'Dark Blue':[37,39]}
rent_map = {1:[4,10,30,90,160,250], 3:[8,20,60,180,320,450],
            6:[12,30,90,270,400,550], 8:[12,30,90,270,400,550], 9:[16,40,100,300,450,600],
            11:[20,50,150,450,625,750], 13:[20,50,150,450,625,750], 14:[24,60,180,500,700,900],
            16:[28,70,200,550,750,950], 18:[28,70,200,550,750,950], 19:[32,80,220,600,800,1000],
            21:[36,90,250,700,875,1050], 23:[36,90,250,700,875,1050], 24:[40,100,300,750,925,1100],
            26:[44,110,330,800,975,1150], 28:[44,110,330,800,975,1150], 29:[48,120,360,850,1025,1200],
            31:[52,130,390,900,1100,1275], 32:[52,130,390,900,1100,1275], 34:[56,150,450,1000,1200,1400],
            37:[70,175,500,1100,1300,1500], 39:[100,200,600,1400,1700,2000]}
cost_map = {1:[60,50], 3:[60,50],
            6:[100,50], 8:[100,50], 9:[120,50],
            11:[140,100], 13:[140,100], 14:[160,180],
            16:[180,100], 18:[180,100], 19:[200,100],
            21:[220,150], 23:[220,150], 24:[240,150],
            26:[260,150], 28:[260,150], 29:[280,150],
            31:[300,200], 32:[300,200], 34:[320,200],
            37:[350,200], 39:[400,200]}

def get_points(color: str, house_count: int = 0, turns: int = 500):
    #Compute the total cost of this color and house combination
    cost = 0
    for i in color_map[color]:
        cost += cost_map[i][0] + house_count*cost_map[i][1]
    
    #What are the odds of a player landing on this color
    land_odds = 0
    for i in color_map[color]:
        land_odds += dpd[i]
    
    #Compute the expected rent earned per turn
    exp_rent_per_turn = 0
    for i in color_map[color]:
        exp_rent_per_turn += (dpd[i] / land_odds)*rent_map[i][house_count]
    exp_rent_per_turn *= land_odds

    # print(f'Expected Rent Per Turn for {color: ^12}: {exp_rent_per_turn}\nExpected Rent to Cost Ratio: {(100*exp_rent_per_turn / cost):.2f}%\n')

    x = [1]
    y = [exp_rent_per_turn / cost]

    t = 2

    while y[-1] < 1:
        x.append(t)
        y.append(t*exp_rent_per_turn / cost)
        t += 1

    return x, y

def plot_color(color: str):
    for i in range(6):
        x, y = get_points(color, i)
        plt.plot(x, y, label=f'{i} Houses')
    plt.xlabel('Number of Turns')
    plt.ylabel('Percentage of Cost Recouped')
    plt.title(f'Time to Recoup for {color}')
    plt.legend()
    plt.show()

def plot_best():
    ci = {'Brown':'brown', 'Light Blue':'lightsteelblue', 'Pink':'pink', 'Orange':'orange', 'Red':'red', 'Yellow':'yellow', 'Green':'green', 'Dark Blue':'b'}
    for c in colors:
        best_i = -1
        best_tcount = 25000
        best_x = []
        best_y = []
        for i in range(6):
            x, y = get_points(c, i)
            if len(x) <= best_tcount:
                best_i = i
                best_tcount = len(x)
                best_x = x
                best_y = y
        plt.plot(best_x, best_y, color=ci[c], label=f'{c}: {best_i} Houses', linewidth=2)
    plt.xlabel('Number of Turns')
    plt.ylabel('Percentage of Cost Recouped')
    plt.title(f'Fastest Times to Recoup')
    plt.legend()
    plt.show()

def main():
    for c in colors:
        s = f'{c} '
        for i in range(6):
            x, y = get_points(c, i)
            s += f'& {x[-1]} '
        s += f'\\\\\\hline'
        print(s)

if __name__ == '__main__':
    main()