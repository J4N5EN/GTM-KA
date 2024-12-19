import csv

input_file = "datasets/5x5_bal_2_moves_before.csv"
min_moves = 0
max_moves = 20

with open(input_file, mode='r', newline='') as infile:
    reader = csv.reader(infile)
    data = list(reader)

data_with_moves = []
for row in data:
    moves = list(map(int, row[:-1]))
    moves_made = sum(abs(m) for m in moves)
    
    if min_moves <= moves_made <= max_moves:
        data_with_moves.append((moves_made, row))

data_with_moves.sort(key=lambda x: x[0])

sorted_data = [item[1] for item in data_with_moves]

output_file = input_file.rsplit('.', 1)[0] + "_filtered_sorted.csv"
print("Writing output to:", output_file)

with open(output_file, mode='w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerows(sorted_data)
