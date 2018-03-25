# CSCI 4144 Assignment 4
# This is the main program. Run with python TreeBuilder.py and answer prompts
import pandas as pd
import sys
import TreeNode as tn
import numpy as np

pd.options.mode.chained_assignment = None  # clears up a false-positive warning with pandas

# reads the file specified by path and returns dataframe
def read_data_file(path):
    fullpath = "./%s" % path
    csv = pd.read_csv(fullpath, delim_whitespace=True)
    return csv


# calculate entropy
# input the data, the target column, the other column to test against if there is one
# returns entropy, number of transactions, most common target value
def calculate_entropy(dataframe, target, sj=None, sj_value=None):


    #if there's an sj, first filter the dataframe
    if sj != None and sj_value != None:
        dataframe = dataframe[dataframe[sj] == sj_value]


    # need to get the highest target value
    target_values = highest_count(dataframe[target].value_counts().to_dict())

    # if we can assume this is binary, just get a list and deal with the two subsequent totals
    values = dataframe[target].value_counts().tolist()

    # if we only got one value, we don't need to do the entropy calc
    # this also means it has a leaf node
    if len(values) < 2:
        return 0.0, len(dataframe), target_values

    # print (float(values[0]) / float(values[1]))
    entropy = -1 * (float(values[0]) / (float(values[0]) + float(values[1]))) * np.log2((float(values[0]) / (float(values[0]) + float(values[1])))) - ((float(values[1])) / (
    float(values[0]) + float(values[1]))) * np.log2(
        (float(values[1])) / (float(values[0]) + float(values[1])))


    # we will need the entropy and also the number of transactions and the most common target value
    return entropy, len(dataframe), target_values

# calculate gain
# returns a dictionary of gains for each attribute, entropies, target values for each attribute value
def calculate_gain(dataframe, target):
    # the target entropy
    target_entropy, num_trans, target_vals = calculate_entropy(df, target)

    # the selected gain
    gains = {}

    # for each column, get the sum of all attribute entropies and subtract it from
    # the target entropy and put them all in a dictionary

    for column in dataframe:
        if column != target:
            col_entropy_sum = 0
            # unique values in the column
            column_vals_to_check = dataframe[column].unique()
            gains[column] = {}
            for sj_val in column_vals_to_check:
                    ent, num, tv = calculate_entropy(dataframe, target, column, sj_val)

                    col_entropy_sum += (float(num)/float(num_trans))*ent
                    gains[column][str(sj_val)] = {'ent': ent, 'num': num, 'tv': tv}

            # the gains
            gains[column]['gain'] = target_entropy - col_entropy_sum

    return gains


# the main tree builder. recursively adds child nodes according to splits
# takes the gains dictionary, the root node, the dataframe, and the target attribute
# returns a tree node
def build_tree(gains, root_node, dataframe, target):
    # print gains
    # print dataframe

    # the attribute with highest gain
    highest = highest_gain(gains)

    # all possible values for highest gain attribute
    vals = dataframe[highest].unique()

    # loop through each value
    for sj_val in vals:
        attrib = "%s=%s" % (highest, sj_val)

        # removes the highest gain from the gains dictionary
        new_gains = gains.copy()
        new_gains.pop(highest, None)


        # if for some reason the value isn't in the gains dictionary, just skip it
        if str(sj_val) not in gains[highest]:
            continue

        # if ent == 0, then it has a leaf node w/ tv as data
        # if not, then we add a new child node w/ value as branch
        if gains[highest][str(sj_val)]['ent'] == 0:
            leaf = tn.TreeNode(target, data=gains[highest][str(sj_val)]['tv'], entropy=gains[highest][str(sj_val)]['ent'],
                               splitAttrib=attrib)
            root_node.addChild(leaf)
        else:
            childnode = tn.TreeNode(target, entropy=gains[highest][str(sj_val)]['ent'],
                               splitAttrib=attrib)           # make a child for this attribute

            # make the subset
            subset_df = dataframe[dataframe[highest] == sj_val]

            # do a leaf node if there are no values in the subset otherwise add a child
            if len(subset_df) > 0:
                # removes the highest gain column
                subset_df.drop(highest, axis=1, inplace=True)
                # recalculuate the gains from this subset
                recalc_gains = calculate_gain(subset_df, target)
                # if we're down to the last non-target column in the subset, add a leaf node
                if len(subset_df.columns) > 1 and recalc_gains != 1.0:
                    root_node.addChild(build_tree(recalc_gains, childnode, subset_df, target))
                else:
                    leaf = tn.TreeNode(target, data=gains[highest][str(sj_val)]['tv'],
                                       entropy=gains[highest][str(sj_val)]['ent'],
                                       splitAttrib=attrib)
                    root_node.addChild(leaf)
            else:
                leaf = tn.TreeNode(target, data=gains[highest][str(sj_val)]['tv'],
                                   entropy=gains[highest][str(sj_val)]['ent'],
                                   splitAttrib=attrib)
                root_node.addChild(leaf)
    return root_node


# highest count of a standard dictionary of counts
def highest_count(count):
    vals = list(count.values())
    keys = list(count.keys())
    return keys[vals.index(max(vals))]

# highest gain from the gains dictionary
def highest_gain(gains):
    highestgain = 0.0
    highestgain_key = ''
    for key,g in gains.items():

        if g['gain'] >= highestgain:
            highestgain_key = key
            highestgain = g['gain']
    return highestgain_key

# find possible binary columns in the data
# returns a list of possible target attributes
def potentialTargets(df):
    targets = []
    for column in df:
        if len(df[column].value_counts().tolist()) < 3:
            targets.append(column)

    return targets


# the main program
if __name__ == "__main__":
    # print the prompts
    print ("\n-----------------------------------------------------")
    print ("\n\tAssignment 4: Decision Tree Alorithm")
    print ("\tJohna Latouf && Chaoran Zhou")
    print ("\n\tType 'quit' to exit or quit.")
    print ("\n-----------------------------------------------------")
    while True:
        # path: the data file name entered
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

    df = read_data_file(path)  # read the file like a csv, put in dataframe
    targets = potentialTargets(df)
    count = 1
    for t in targets:
        print "%s. %s" % (count, t)
        count += 1
            # path: the data file name entered

    while True:
        target_int = raw_input("\nSelect the target attribute by number (eg. 1): ")
        if target_int == "quit":
            sys.exit(0)
        if target_int.isdigit() and int(target_int) <= len(targets) and int(target_int) > 0:
            break
        else:
            print "You must select a valid digit"
            continue

    target = targets[int(target_int)-1]

    df = read_data_file(path)  # read the file like a csv, put in dataframe

    # start the tree
    root = tn.TreeNode(target=target)

    # get the first set of information gains
    gains = calculate_gain(df, target)

    # build the tree
    tree = build_tree(gains=gains, root_node=root, dataframe=df, target=target)
    # print the tree
    tree.printTree()
