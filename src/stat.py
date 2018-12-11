import matplotlib.pyplot as plt
import numpy as np

N = 3
pos = list(range(5))
reel = (127, 511, 988)
ok = (92, 482, 915)
false = (50, 117, 22)
detected = (ok[0]+false[0], ok[1]+false[1], ok[2]+false[2])

ind = np.arange(N)
width = 0.35
plt.bar(ind, reel, width, label='Réel')
plt.bar(ind + width, detected, width,label='Détecté')
plt.bar(ind + 2*width, ok, width,label='Vrai')
plt.bar(ind + 3*width, false, width,label='Faux')

plt.ylabel('Scores')
plt.title('Scores by group and gender')
print('ind',ind)
plt.xticks(ind + width, ('Bas', 'Moyen', 'Élevé'))
# plt.set_xticks([p + 1.5 * width for p in pos])
plt.legend(loc='best')
plt.savefig('lastPred2.png')
