import numpy as np
import pandas as pd
from scipy import stats, integrate
import matplotlib.pyplot as plt

import seaborn as sns
sns.set(color_codes=True)

cc = [350, 627, 729, 435, 387, 364, 407, 458, 528, 616, 401, 434, 430, 244, 682, 523, 628, 693, 1063, 587, 387, 608, 1033, 486, 509, 574, 375, 487, 956, 1098, 673, 331, 257, 888, 545, 1529, 703, 631, 1223, 527, 1255, 1065, 583, 361, 507, 898, 1145, 500, 473, 534, 517, 509, 1032, 279, 643, 925, 1061, 774, 708, 426, 524, 587, 912, 450, 1354, 467, 507, 880, 611, 494, 508, 514, 592, 498, 741, 841, 508, 981, 714, 987, 659, 337, 563, 1002, 657, 449, 657, 1249, 440, 418, 425, 1149, 293, 547, 1582, 669, 639, 1048, 725, 513]
sb = [938, 565, 610, 773, 747, 542, 340, 596, 794, 560, 729, 737, 827, 594, 877, 840, 1242, 968, 763, 976, 931, 523, 474, 340, 252, 287, 718, 803, 657, 950, 638, 821, 561, 1243, 681, 818, 942, 759, 477, 665, 677, 633, 768, 833, 504, 687, 688, 627, 880, 709, 599, 552, 768, 470, 420, 443, 1399, 508, 505, 355, 1295, 599, 689, 739, 393, 580, 819, 1325, 612, 863, 570, 606, 854, 1054, 858, 993, 731, 513, 726, 561, 794, 674, 605, 656, 527, 876, 547, 777, 460, 603, 894, 749, 924, 353, 569, 788, 691, 787, 509, 888]

plt.subplot(1, 2, 1)
plt.title('Coverage Contours')
sns.distplot(cc, bins=50,rug = True);
plt.xlabel('Game completion time (units)')
plt.ylabel('Normalized frequency')


plt.subplot(1, 2, 2)
plt.title('Sbandit')
sns.distplot(sb, bins=50,rug = True);
plt.xlabel('Game completion time (units)')
plt.ylabel('Normalized frequency')
plt.tight_layout()
plt.show()