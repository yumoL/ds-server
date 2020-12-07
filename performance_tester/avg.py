"""
calculate the average of a file
"""
filename = '1000_1000.txt'

total = 0
line = 1
with open(filename, 'r') as f:
    content = f.readlines()

content = [float(x.strip()) for x in content]
print(sum(content)/len(content))