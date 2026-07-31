import json

bits = 1044720
sigma = []
for i in range(20):
    if (bits & (1 << i)) != 0:
        sigma.append(1)
    else:
        sigma.append(-1)
        
sides = [2, 4, 10, 17]
for s in sides:
    print(f"Side {s} has sign {sigma[s]}")
