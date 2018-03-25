import pandas as pd
import sys
#import os
import itertools

# reads the file specified by path and returns dataframe
def read_data_file(path):
    fullpath = "./%s" % path
    csv = pd.read_csv(fullpath, delim_whitespace=True)
    return csv


# get count for column into dictionary
def generate_column_count(df, column, min_sup, total_rows):
    counts = df[column].value_counts(sort=True, ascending=True)
    return counts[counts/total_rows >= min_sup].to_dict()


# get all the column counts into dictionary of dictionaries
def generate_counts(df, min_sup, total_rows):
    counts = []
    for column in df:
        df[column] = column + ' ' + df[column].astype(str)
        counts.append(generate_column_count(df, column, min_sup, total_rows))
    return counts


# combine each thing with every other thing
def combine_items(counts):

    new_item_combo = []
    finished_col = []
    for column in counts:
        for item_name, count in column.items():
            item_header = item_name.split(' ')[0]

            for combo_col in counts:
                for combo_item, combo_count in combo_col.items():
                    combo_item_header = combo_item.split(' ')[0]
                    if (combo_item_header not in finished_col and item_header != combo_item_header):
                        combo = [item_name, combo_item]
                        new_item_combo.append(combo)
            finished_col.append(item_header)

    df_items = pd.DataFrame(new_item_combo)

    return df_items



# Uses itertools to get all combinations possible
def all_combine_items(counts, k):

    all_items = []
    for c in counts:
        item = c.split(",")
        all_items.extend(item)
    all_items = list(set(all_items))

    output_list = list(itertools.combinations(all_items, k))


    whole = pd.DataFrame(output_list)

    return whole


# check rows against combos
def count_combos(df, combo):
    combo_counts = {}
    for index, row in combo.iterrows():
        col1 = row[0].split(' ')[0]
        col2 = row[1].split(' ')[0]
        dfcombo = df.loc[(df[col1]==row[0]) & (df[col2]==row[1])]
        combo_counts[row[0] + ',' + row[1]] = len(dfcombo)
    return combo_counts


def all_combo_counts(df, combo, min_sup, total_rows):
    combo_counts = {}
    for index, row in combo.iterrows():
        #col_items = []
        dfcombo = df
        for r in row:
            dfcombo = dfcombo.loc[(df[r.split(' ')[0]] == r)]

        if (float(len(dfcombo))/total_rows >= min_sup):
            combo_counts[','.join(sorted(row))] = len(dfcombo)

    return combo_counts


def generate_rules(count, total_rows, min_conf):
    rules = []

    # for every set that has been counted, slice it up and generate all possible rules
    for key, c in count.items():
        items = key.split(",")
        if len(items) < 2:
            continue

        # make all possible combos and then test
        combo_lists = list(itertools.permutations(items, len(items)))
        # for every item in a set, do a rule
        for item in combo_lists:
            counttimes = 0
            for x in range(len(item)):
                for y in range(len(item)):
                    # first subset for testing confidence
                    first_items = [i for i in item[x:x+y]]
                    conf_first_items = ",".join(sorted(first_items))


                    first_items = sorted(first_items)
                    if len(first_items) < 1:
                        continue
                    # all the items not in the first subset
                    conf_item = [m for i, m in enumerate(item) if i not in range(x, x+y)]
                    # math
                    sup = float(c) / float(total_rows)


                    conf = float(c) / float(count[conf_first_items])
                    if conf >= min_conf:
                        output_string = "(Support=%s, Confidence=%s)\n{ %s } ----> { %s }\n" % (
                            "{:1.3f}".format(sup), "{:1.3f}".format(conf), ",".join(sorted(first_items)), ",".join(sorted(conf_item)))
                        if output_string not in rules:
                            rules.append(output_string)
                            counttimes += 1
            # print "%s had %s " % (item, counttimes)




    return rules


# testing
if __name__ == "__main__":

    print ("\n-----------------------------------------------------")
    print ("\n\tAssignment 3: Association Rule Mining")
    print ("\tThe Apriori Algorithm Implementation")
    print ("\tJohna Latouf && Chaoran Zhou")
    print ("\n\tType 'quit' to exit or quit.")
    print ("\n-----------------------------------------------------")
    while True:
        #path: the data file name entered
        path = raw_input("\nWhat is the name of the file containing your data? (eg: data1) ")
        if path == "quit":
            sys.exit(0)
        try:
            open(path, 'r')
            break;
        except IOError:
            print("\nCan't open the file.")
            continue;
        except OSError:
            print("\nCan't open the file.")
            continue;

    while True:
        # the min support entered
        min_sup = raw_input("\nPlease enter the minimum Support rate: (eg: .25) ")
        if min_sup == "quit":
            sys.exit(0)
        try: 
            min_sup = float(min_sup)
            if min_sup < 0 or min_sup > 1:
                print("\nA valid minimum support rate is between 0.00-1.00 (eg: .25).")
                continue;
            break;
        except ValueError:
            print("\nA valid minimum support rate is a float between 0.00-1.00 (eg: .25).")
            continue;

    while True:
        # min confidence entered            
        min_conf = raw_input("\nPlease enter the minimum Confidence rate: (eg: .5) ")
        if min_conf == "quit":
            sys.exit(0)        
        try: 
            min_conf = float(min_conf)
            if min_conf < 0 or min_conf > 1:
                print("\nA valid minimum confidence rate is between 0.00-1.00")
                continue;
            break;
        except ValueError:
            print("\nA valid minimum confidence rate is a float between 0.00-1.00 (eg: .5).")
            continue;

    
    rules = []                                  # this will hold rules at the end
    save_counts = {}                            # saves the counts for calculating rules

    df = read_data_file(path)                   # read the file like a csv, put in dataframe
    total_rows = len(df)                        # the length of df gives row total

    #print (df)                                    # print it to look nice

    # first generate counts of individual bits
    counts = generate_counts(df, min_sup, total_rows)
    counts_dict = {}

    # put the counts in a better format
    for c in counts:
        counts_dict.update(c)

    # save the counts for making rules
    save_counts.update(counts_dict)

    #combine the counts
    morecombos = combine_items(counts)

    # k is the length of combination rows
    k = 1
    # This loop checks the subsequent
    while True:
        # count all the sets
        better_count = all_combo_counts(df, morecombos, min_sup, total_rows)
        # save the counts for rule generation later
        save_counts.update(better_count)
        # make new combos with the items that are in subsets >= min_sup
        morecombos = all_combine_items(better_count, k)
        k += 1
        if len(better_count) < 1:
            break

    # generating the rules
    rules = generate_rules(save_counts, total_rows, min_conf)

    # printing the rules
    print ("\n-----------------------------------------------------")
    print ("\nResults:")
    print ("\nThe selected measure: Min_Support = %s , Min_Confidence = %s" % (min_sup, min_conf))
    print ("\nTotal rows in the original set: %s " % total_rows)
    print ("\nTotal Rules discovered: %s " % len(rules))
    print ("\n-----------------------------------------------------")

    
# TODO - need to write all the information below to the output file 'Rules'!
    # save rules to the output file 'Rules'
    '''
    print ("Summary:")
    print ("Total rows in the original set: %s" % total_rows)
    print ("Total Rules discovered: %s" % len(rules))
    print ("The selected measure: Support = %s" % min_sup)
    print ("Confidence = %s" % min_conf)
    print ("-----------------------------------------------------")
    rulenumber = 1
    for r in rules:
        print ('Rule #%s: %s' % (rulenumber,r))
        rulenumber += 1
    '''

    rules_file = open("Rules.txt", "w")

    rules_file.write(
        'Summary:\nTotal rows in the original set: %s\nTotal Rules discovered: %s\nThe selected measure: Support = %s\nConfidence = %s\n-----------------------------------------------------\n\n' % (
    total_rows, len(rules), min_sup, min_conf))
    rulenumber = 1
    for r in rules:
        rule_output = 'Rule #%s: %s\n' % (rulenumber, r)
        rules_file.write(rule_output)
        rulenumber += 1
    rules_file.close()

    print ("\nRules file created successfully: 'Rules.txt'.")
    print ("\n********************Program End**********************")