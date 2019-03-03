import csv
import json
import os


def split_csv_to_json(filehandler, delimiter=',', row_limit=100,
                      output_name_template='output_%s.csv', output_path='.'):
    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_limit = row_limit
    current_out_path = os.path.join(
        output_path,
        output_name_template % current_piece
    )
    headers = reader.__next__()
    data = []
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(
                output_path,
                output_name_template % current_piece
            )
            data.clear()
        data.append({
            headers[0]: row[0],
            headers[1]: row[1]
        })
        with open(current_out_path, 'w') as outfile:
            json.dump(data, outfile)


with open('memes.csv', newline='') as csvfile:
    split_csv_to_json(filehandler=csvfile,
                      row_limit=30,
                      output_path='./json',
                      output_name_template='memes_%s.json')