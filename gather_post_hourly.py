# This file gets data on the hourly data to get an idea of which hour to select from
import csv
DELIMITER = ","
QUOTECHAR = '"'
mapping = {8: 'score'}
for i in range(2,19):
    if i % 2 == 0 and i!=8:
        mapping[i] = 'score_' + str(i)
posts = []
with open('reddit_posts_18.csv') as f:
    data = csv.reader(f, delimiter=DELIMITER, quotechar=QUOTECHAR)
    for i,line in enumerate(data):
        if i==0:
            header = line
            indexing = {}
            values = {}
            for key, value in mapping.items():
                indexing[key] = header.index(value)
                values[key] = 0
            continue
        else:
            if line[-1] == "True":
                add = True
                for key, value in indexing.items():
                    if line[value] == "":
                        add = False
                if add:
                    posts.append(line)


for line in posts:
    for key, value in indexing.items():
        values[key] += int(line[value])

for key, value in sorted(values.items()):
    print(key,value)