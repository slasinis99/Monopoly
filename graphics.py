import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

# Define the size of the large square
large_square_size = 11

# Define the size of the smaller squares
small_square_size = 1

# Define the number of small squares along each side (excluding corners)
num_squares_side = 8

# Create the figure and axis
fig, ax = plt.subplots(figsize=(8, 8))

# Plot the large square
large_square = plt.Rectangle((0, 0), large_square_size, large_square_size, color='lightgrey', alpha=0.5)
ax.add_patch(large_square)

# Store the Coordinates
coords = [(10,0), (9,0), (8,0), (7,0), (6,0), (5,0), (4,0), (3,0), (2,0), (1,0), 
          (0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6), (0,7), (0,8), (0,9), (0,10),
          (1,10), (2,10), (3,10), (4,10), (5,10), (6,10), (7,10), (8,10), (9,10), (10,10),
          (10,9), (10,8), (10,7), (10,6), (10,5), (10,4), (10,3), (10,2), (10,1)]

# Distributions overall measured
percent_overall = [0.03068198305881336, 0.021318785649411108, 0.018977124066241857, 0.02163256982779374, 0.023291431167145188, 0.029657534357104345, 0.0226415458778483, 0.0086648738644404, 0.023247995699702394, 0.02305190574028933, 0.06192479118622115, 0.02705759598513173, 0.026050809067410745, 0.02372489640583919, 0.02464332713076307, 0.029210179340047347, 0.027898352955063783, 0.026166969988195333, 0.029323226391605017, 0.030828576495195548, 0.028825482192633877, 0.028349894382660678, 0.010492072926506644, 0.0273657639025349, 0.031870331206599024, 0.030659709562056145, 0.027071954961948325, 0.02678103611193465, 0.02807162271019862, 0.02585167737592261, 0.0, 0.026759822724342967, 0.02623736188141656, 0.023840159602791552, 0.024987224425992258, 0.024314035460016474, 0.008661145908522981, 0.021842483721233326, 0.02179491326015674, 0.02622883342826874]

percent_steady = [0.03057861328125, 0.0213470458984375, 0.01898193359375, 0.021636962890625, 0.0232391357421875, 0.0296173095703125, 0.0225372314453125, 0.008636474609375, 0.02313232421875, 0.0229644775390625, 0.062744140625, 0.0269927978515625, 0.0260009765625, 0.023712158203125, 0.024627685546875, 0.0291748046875, 0.027923583984375, 0.0261688232421875, 0.02935791015625, 0.0308380126953125, 0.028839111328125, 0.0283660888671875, 0.0104827880859375, 0.0273284912109375, 0.031829833984375, 0.0306549072265625, 0.027069091796875, 0.026763916015625, 0.028045654296875, 0.0258331298828125, 0.0, 0.0267486572265625, 0.026214599609375, 0.0240020751953125, 0.02496337890625, 0.0243072509765625, 0.00865936279296875, 0.021881103515625, 0.02178955078125, 0.0262908935546875]

percent_winners = [0.029816299142573128, 0.0206886046383454, 0.018647493861565095, 0.021621502966243333, 0.022625875967833203, 0.03006433046055043, 0.023525877012144453, 0.009051456824548876, 0.024031317740632312, 0.02379798961504942, 0.06068193879667476, 0.02784533176451947, 0.02577262539522965, 0.024144683199898657, 0.025011579873406402, 0.029211841140555923, 0.028084990842159513, 0.026337115564400087, 0.02941993420957457, 0.030820583392498643, 0.028732996327485712, 0.028318821893840405, 0.01042894182307693, 0.027254097760490793, 0.0317812018235627, 0.030282038293207275, 0.026952519605020778, 0.02672433907597033, 0.027876454014819103, 0.0259000136174637, 0.0, 0.02656982242833251, 0.025895516866469837, 0.023672790600536064, 0.024334079251627033, 0.023525344502158336, 0.008307658709498142, 0.023846862198219566, 0.020208606053638608, 0.02818652274617885]

percent_bankrupt = [0.030643225311269284, 0.02119572666068827, 0.018402233642019993, 0.021879324416816656, 0.023647770486351374, 0.030045107284941863, 0.022563840748622475, 0.008994786978646977, 0.023553313766975514, 0.023472802696520655, 0.06325502092943366, 0.027306948012478852, 0.02653313151112275, 0.023746840960834334, 0.024649654714709705, 0.030086390998626415, 0.028127570119944063, 0.0266477968954021, 0.02948655064290381, 0.0309405306799579, 0.029378127397887005, 0.028497797871388758, 0.010655248214283665, 0.027383158478625734, 0.031871726334593904, 0.03115275297652444, 0.02694616697680774, 0.026648527580600056, 0.028326379123948114, 0.025534295283875897, 0.0, 0.026481357245667532, 0.025988917175684592, 0.023801454460201613, 0.024823818750822672, 0.024509728499300994, 0.008703932516420322, 0.019414848504428317, 0.02216372797258135, 0.022539467178090633]

percent_win_v_overall = []
percent_overall_v_steady = []
for i in range(len(percent_overall)):
    percent_win_v_overall.append(percent_winners[i]-percent_overall[i])
    percent_overall_v_steady.append((percent_steady[i]-percent_overall[i]))
# Space names
board_layout = ["Go","Med Ave","Com Ches","Balt Ave","Inc Tax","Read Rl","Orient","Chance","Vermont","Conn Ave","Jail","St Chas","Elec Co","States","Virginia","Penn Rl","St James","Com Ches","Tenn Ave","New York","Free Pk","Kentucky","Chance","Indiana","Illinois","B&O Rl","Atlantic","Ventnor","Water W","Marvin G","Go Jail","Pacific","North C","Com Ches","Penn Ave","Short Ln","Chance","Park Pl","Lux Tax","Boardwalk"]

data = percent_overall_v_steady

# Define the colormap (using 'inferno' or PuRd colormap)
cmap = plt.cm.OrRd

# Normalize the numbers to range from 0 to 1
if data is percent_win_v_overall:
    norm = Normalize(vmin=min(data), vmax=max(data))
else:
    norm = Normalize(vmin=min(data), vmax=max(data))

# Create a scalar mappable
sm = ScalarMappable(norm=norm, cmap=cmap)

# Map the numbers to colors

colors = [sm.to_rgba(number) for number in data]

for i, coord in enumerate(coords):
    small_square = plt.Rectangle(coord, small_square_size, small_square_size, color=colors[i])
    ax.add_patch(small_square)
    ax.text(coord[0]+0.5, coord[1]+0.5, f'{board_layout[i]}\n{f"{100*data[i]:0.2f}%"}', color='black', ha='center', va='center', fontsize=8)

# Set axis limits and labels
ax.set_xlim(0, large_square_size)
ax.set_ylim(0, large_square_size)
# ax.set_xticks(np.arange(0, large_square_size + 1, 1))
# ax.set_yticks(np.arange(0, large_square_size + 1, 1))
ax.set_xticklabels("")
ax.set_yticklabels("")
ax.set_aspect('equal')

# Show the plot
plt.title('Steady State vs Measured Space Distribution')
# plt.grid(True)
plt.tick_params(left = False, bottom = False)
plt.tight_layout()
plt.show()
