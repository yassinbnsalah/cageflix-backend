import gzip
import csv



def get_nicolas_cage_nconst(filepath="datasets/name.basics.tsv.gz"):
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['primaryName'] == 'Nicolas Cage':
                return row['nconst']
            
            