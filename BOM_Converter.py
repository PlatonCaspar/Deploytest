import csv
import os

'''print("Please enter the path of the BOM file")
file_path = input()
print(file_path)
print(os.path.exists(file_path))
with open(file_path, 'rt') as bom:
    reader = csv.reader(bom, delimiter=';')
    for row in reader:
        print (row[2])
'''


def read_csv(bom_file):
    out = list()
    reader = csv.reader(bom_file, delimiter=';')
    
    for row in reader:
        if any(i.isdigit() for i in row[0]):
            print(row)
            out.append((row[6],row[0]))
    return out