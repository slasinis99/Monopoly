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
percent_overall = [0.030134237256964944, 0.020679554796452136, 0.018307393507967618, 0.021069143856236844, 0.022718558235145965, 0.028933991050541483, 0.02209175015852867, 0.008469995389910926, 0.022696494036356082, 0.022484313841972223, 0.06054407483991399, 0.026411163629744376, 0.02540048470192928, 0.023152275692510438, 0.02398615223159299, 0.028529297833731763, 0.027216218087161615, 0.025331173082694048, 0.02863320750290192, 0.03011740030945905, 0.028082122370299115, 0.027666656972666587, 0.010206222571912177, 0.02662880211414301, 0.031042883705297508, 0.029867965119736255, 0.026355656574673494, 0.02614864587189093, 0.02736503590962793, 0.025175135299890728, 0.02562366811586673, 0.026029632045695764, 0.025568969696353593, 0.023017840031035432, 0.024295224293699437, 0.02367907287853956, 0.00844564968365455, 0.021236675815896673, 0.021186309372585737, 0.025470951514818433]

percent_steady = [0.02979520722881103, 0.020805810042658395, 0.018494950385630735, 0.021077432284862006, 0.022641181512666038, 0.02884773292847713, 0.021968294915567718, 0.008415095684942616, 0.02254430788094695, 0.0223854477518096, 0.06084769540815935, 0.02628900075531833, 0.025329989961047978, 0.023103669895367808, 0.023995608784316627, 0.028441299609675143, 0.027205092518622756, 0.02550458037447871, 0.02860307059207864, 0.030051798414379813, 0.028094495999895733, 0.02762496669336098, 0.01021074036347828, 0.02664230499230296, 0.031034797740052703, 0.029862629875221876, 0.02637073226720803, 0.026085074391013797, 0.027340215068984992, 0.025171769804295082, 0.0256486103274277, 0.026053334613644907, 0.025532737031173154, 0.02338760421447785, 0.02431584558744104, 0.023687639175045076, 0.008438323334401228, 0.02131637603900079, 0.021221955829141454, 0.025612579722655064]

percent_winners = [0.028914462052782152, 0.020077790992960236, 0.018071940595969012, 0.020865344434086597, 0.022225079558970073, 0.028985181137291458, 0.02297727345784178, 0.008666302356231316, 0.023536597126233565, 0.02297727345784178, 0.05969012182969559, 0.0275065093702787, 0.024809540647401075, 0.02386769102189077, 0.02391269407566942, 0.028252274261467744, 0.02766080555466264, 0.02499919637403967, 0.028888746022051496, 0.02978559259378315, 0.029026969687228777, 0.02729113761290945, 0.010029251984956121, 0.02683789257128162, 0.030836735349898742, 0.02917483686393005, 0.026137130733871226, 0.026436079591115113, 0.027455077308817383, 0.025558520042431452, 0.024748465074415762, 0.025568163553955445, 0.0252627856890289, 0.022636536050660582, 0.02395769712944807, 0.02251438490468996, 0.007978398534186248, 0.02371339483750683, 0.020045645954546915, 0.028120479603973125]

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
