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
percent_overall = [0.02934031535247648, 0.02012685876465997, 0.017859397769063416, 0.020557118663021547, 0.0220495917154309, 0.035198669401759586, 0.021503459272245288, 0.008262781594123038, 0.022116341236264696, 0.021900777848636938, 0.05548012121250649, 0.030012433904248823, 0.02741267009930653, 0.022432462343590125, 0.023426770140945515, 0.030429690649201216, 0.026490024125183958, 0.024674494950297613, 0.02779409593264251, 0.029143245338586223, 0.027474218358776652, 0.026913926926323266, 0.009985265982392574, 0.02587338569462412, 0.03454937860819447, 0.032297521396688934, 0.02565406584045593, 0.02546913210308091, 0.02823620314855467, 0.024422811692088795, 0.02490624003994569, 0.025459885416212157, 0.024801347935778293, 0.02247725098311064, 0.023687989044987732, 0.023051701404831797, 0.008120613783515989, 0.020542381755824474, 0.020569832857466077, 0.029295526712955967]

percent_steady = [0.02978677719743324, 0.020799923403570657, 0.018489717563758272, 0.021071468795024192, 0.022634775587407112, 0.028839570968337103, 0.02196207937177128, 0.008412714781190999, 0.022537929364383286, 0.02237911418193358, 0.06111341208315525, 0.026281562743575168, 0.025322823284591206, 0.023097133117131467, 0.023988819647613284, 0.028433252642715207, 0.02719739531478032, 0.025497364300726195, 0.028594977854856138, 0.030043295785025816, 0.02808654715493541, 0.027617150693483975, 0.01020785141355444, 0.02663476701932168, 0.03102601698827798, 0.02985418076778865, 0.026363271130966873, 0.026077694076659205, 0.02733247963458653, 0.025164647893457036, 0.0256413535029258, 0.026045963279503738, 0.0255255129909884, 0.023380987102005178, 0.024308965845350125, 0.023680937172941945, 0.008435935858793535, 0.021310344944218008, 0.02121595144890124, 0.025605333092380927]

# Space names
board_layout = [
    "Go",
    "Med Ave",
    "Com Ches",
    "Balt Ave",
    "Inc Tax",
    "Read Rl",
    "Orient",
    "Chance",
    "Vermont",
    "Conn Ave",
    "Jail",
    "St Chas",
    "Elec Co",
    "States",
    "Virginia",
    "Penn Rl",
    "St James",
    "Com Ches",
    "Tenn Ave",
    "New York",
    "Free Pk",
    "Kentucky",
    "Chance",
    "Indiana",
    "Illinois",
    "B&O Rl",
    "Atlantic",
    "Ventnor",
    "Water W",
    "Marvin G",
    "Go Jail",
    "Pacific",
    "North C",
    "Com Ches",
    "Penn Ave",
    "Short Ln",
    "Chance",
    "Park Pl",
    "Lux Tax",
    "Boardwalk"
]

# Define the colormap (using 'inferno' colormap)
cmap = plt.cm.PuRd

# Normalize the numbers to range from 0 to 1
norm = Normalize(vmin=0, vmax=max(percent_steady))

# Create a scalar mappable
sm = ScalarMappable(norm=norm, cmap=cmap)

# Map the numbers to colors
colors = [sm.to_rgba(number) for number in percent_steady]

for i, coord in enumerate(coords):
    small_square = plt.Rectangle(coord, small_square_size, small_square_size, color=colors[i])
    ax.add_patch(small_square)
    ax.text(coord[0]+0.5, coord[1]+0.5, f'{board_layout[i]}\n{f"{100*percent_steady[i]:0.2f}%"}', color='black', ha='center', va='center', fontsize=8)

# Set axis limits and labels
ax.set_xlim(0, large_square_size)
ax.set_ylim(0, large_square_size)
# ax.set_xticks(np.arange(0, large_square_size + 1, 1))
# ax.set_yticks(np.arange(0, large_square_size + 1, 1))
ax.set_xticklabels("")
ax.set_yticklabels("")
ax.set_aspect('equal')

# Show the plot
plt.title('Steady State Player Distribution')
# plt.grid(True)
plt.tick_params(left = False, bottom = False)
plt.tight_layout()
plt.show()
