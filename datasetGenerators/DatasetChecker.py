import csv
import os

def find_duplicates(input_filename):
    seen = set()
    duplicates = []

    with open(input_filename, 'r', newline='') as infile:
        reader = csv.reader(infile)
        for row in reader:
            row_tuple = tuple(row)
            if row_tuple in seen:
                duplicates.append(row)
            else:
                seen.add(row_tuple)
    return duplicates

def remove_duplicates(input_filename):
    seen = set()
    unique_rows = []

    # Read all rows and filter out duplicates
    with open(input_filename, 'r', newline='') as infile:
        reader = csv.reader(infile)
        for row in reader:
            row_tuple = tuple(row)
            if row_tuple not in seen:
                unique_rows.append(row)
                seen.add(row_tuple)

    # Write back only unique rows
    with open(input_filename, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        for row in unique_rows:
            writer.writerow(row)


if __name__ == "__main__":
    # input_csv = 'games.csv'
    name = input("File name of simulated board?\n")
    input_csv = f"datasets/{name}.csv"
    
    duplicates = find_duplicates(input_csv)

    num_duplicates = len(duplicates)
    if num_duplicates == 0:
        print("No duplicates found.")
    else:
        print(f"{num_duplicates} duplicates found.")
        answer = input("Do you want to remove duplicates from the CSV? [y/N]: ").strip().lower()
        if answer == 'y':
            remove_duplicates(input_csv)
            print("Duplicates removed.")
        else:
            print("No changes made to the file.")
