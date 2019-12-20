import csv
import random
DELIMITER = ","
QUOTECHAR = '"'
DIRECTORY = "data/"
RATIO = 0.9

if __name__ == "__main__":
    lines = {}
    with open('reddit_posts_18.csv') as f:
        data = csv.reader(f, delimiter=DELIMITER, quotechar=QUOTECHAR)
        for i,line in enumerate(data):
            if i==0:
                lines['header'] = line
                try:
                    subreddit_index = line.index('subreddit')
                except Exception as e:
                    print("No specified Subreddit")
            else:
                sub = line[subreddit_index]
                if sub not in lines:
                    lines[sub] = []
                lines[sub].append(line)
    all = []
    for key, value in lines.items():
        if key == "header":
            continue
        all += value
        random.shuffle(value)
        length = int(len(value)*RATIO)

        with open(DIRECTORY + key + "_train.csv", 'w') as f:
            writer = csv.writer(f, delimiter=DELIMITER, quotechar=QUOTECHAR)
            writer.writerow(lines['header'])
            for line in value[:length]:
                writer.writerow(line)

        with open(DIRECTORY + key + "_test.csv", 'w') as f:
            writer = csv.writer(f, delimiter=DELIMITER, quotechar=QUOTECHAR)
            writer.writerow(lines['header'])
            for line in value[length:]:
                writer.writerow(line)

    random.shuffle(all)
    length = int(len(value)*RATIO)
    with open(DIRECTORY + "all_train.csv", 'w') as f:
        writer = csv.writer(f, delimiter=DELIMITER, quotechar=QUOTECHAR)
        writer.writerow(lines['header'])
        for line in all[:length]:
            writer.writerow(line)

    with open(DIRECTORY + "all_test.csv", 'w') as f:
        writer = csv.writer(f, delimiter=DELIMITER, quotechar=QUOTECHAR)
        writer.writerow(lines['header'])
        for line in all[length:]:
            writer.writerow(line)

