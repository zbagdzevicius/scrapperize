import csv

with open("2018-10-13_memes.csv", 'r') as f:
    reader = csv.reader(f, delimiter=',')
    title = next(reader)

    lines = []
    for line in reader:
        image = line[1]
        line[1] = f'{image[:-1]}.jpg'
        lines.append(line)
with open("memes.csv", 'w', newline='') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(title)
    writer.writerows(lines)