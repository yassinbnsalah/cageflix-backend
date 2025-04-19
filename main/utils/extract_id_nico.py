import gzip
import csv


# Function to extract the nconst of Nicolas Cage from the name.basics.tsv.gz file
# The function reads the file line by line, looking for the row where the primaryName is 'Nicolas Cage'
def get_nicolas_cage_nconst(filepath="datasets/name.basics.tsv.gz"):
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['primaryName'] == 'Nicolas Cage':
                return row['nconst']
            
            