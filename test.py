from itertools import *

for k, i in enumerate(product('0123456789', repeat=6)):
    s=''
    for j in i:
        s+=j
    print(s)
    if k == 100000:
        print('MORE 100000')
        break