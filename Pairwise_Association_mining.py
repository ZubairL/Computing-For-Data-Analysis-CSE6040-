import pandas as pd
from itertools import combinations
from collections import defaultdict

#Code to Run data on VS Code 

def on_vocareum():
    import os
    return os.path.exists('.voc')

def download(file, local_dir="", url_base=None, checksum=None):
    import os, requests, hashlib, io
    local_file = "{}{}".format(local_dir, file)
    if not os.path.exists(local_file):
        if url_base is None:
            url_base = "https://cse6040.gatech.edu/datasets/"
        url = "{}{}".format(url_base, file)
        print("Downloading: {} ...".format(url))
        r = requests.get(url)
        with open(local_file, 'wb') as f:
            f.write(r.content)            
    if checksum is not None:
        with io.open(local_file, 'rb') as f:
            body = f.read()
            body_checksum = hashlib.md5(body).hexdigest()
            assert body_checksum == checksum, \
                "Downloaded file '{}' has incorrect checksum: '{}' instead of '{}'".format(local_file,
                                                                                           body_checksum,
                                                                                           checksum)
    print("'{}' is ready!".format(file))
    
if on_vocareum():
    DATA_PATH = "./resource/asnlib/publicdata/"
else:
    DATA_PATH = ""
datasets = {'groceries.csv': '0a3d21c692be5c8ce55c93e59543dcbe'}

for filename, checksum in datasets.items():
    download(filename, local_dir=DATA_PATH, checksum=checksum)

with open('{}{}'.format(DATA_PATH, 'groceries.csv')) as fp:
    groceries_file = fp.read()
print (groceries_file[0:250] + "...\n... (etc.) ...") # Prints the first 250 characters only
print("\n(All data appears to be ready.)")



#Given csv_str, a string where each receipt is a line and the items within each receipt 
#are separated by a comma, this function returns a list of sets. Each set should be a single receipt, 
#and each element of the set should be an item contained within that receipt. 

def make_itemsets_csv(csv_str):
   
    lines = csv_str.split('\n')
    data = []
    for line in lines:
        line = line.split(',')
        data.append(set(line))
    return data


make_itemsets_csv(groceries_file)

#creates the item pairs using the combinations method. This method 
#is able to generate all combinations in pairs of the itemset. These 
# two functions don't return anything because they will be used in the
#final function
def update_pair_counts (pair_counts, itemset):
    """
    Updates a dictionary of pair counts for
    all pairs of items in a given itemset.
    """
    assert type (pair_counts) is defaultdict
    item_pairs = combinations(itemset, 2)
    
    # Update pair_counts for each item-pair
    for a,b in item_pairs:
        pair_counts[(a,b)] += 1
        pair_counts[(b,a)] += 1


def update_item_counts(item_counts, itemset):
    for letter in itemset:
        item_counts[letter] += 1


#Filters out any pairs that have a confidence level lower than the threshold
def filter_rules_by_conf(rules, threshold):
    filtered_rules = {}
    for pair, confidence in rules.items():
        if confidence >= threshold:
            filtered_rules[pair] = confidence
    return filtered_rules


#MAIN FUNCTION

def create_rules_from_source(source, itemset_maker, conf_threshold=0, min_count=0):
    # Confidence threshold
    THRESHOLD = 0.5

    # Only consider rules for items appearing at least `MIN_COUNT` times.
    MIN_COUNT = 10
    pair_counts = defaultdict(int)
    item_counts = defaultdict(int)

    # Splitting the data into transactions
    receipts = make_itemsets_csv(source)

    for receipt in receipts:
        update_pair_counts(pair_counts, receipt)
        update_item_counts(item_counts, receipt)


    new_item_counts = {}
    for key, value in item_counts.items():
        if value >= min_count:
            new_item_counts[key] = value
    item_counts = new_item_counts


    rules = {}
    for key, value in pair_counts.items():
        if key[0] in item_counts:
            rules[key] = value/item_counts[key[0]]


    filtered_rules = {}
    filtered_rules=filter_rules_by_conf(rules, conf_threshold)

    return filtered_rules
    
grocery_rules = create_rules_from_source(groceries_file, make_itemsets_csv, 0.5, 10)
print('Source: `groceries_file`; Itemset Maker: `make_itemsets_csv`; Confidence Threshold: 0.5; Min Count: 10')

print(grocery_rules)