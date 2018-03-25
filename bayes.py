import pandas as pd
import numpy as np
import sys

# reads the file specified by path and returns dataframe
def read_data_file(path):
    fullpath = "./%s" % path
    csv = pd.read_csv(fullpath, delim_whitespace=True)
    return csv


# break the dataframe up by target values
def count_split(df, target):

    dataframes = {}
    for val in df[target].unique():
        key = "%s=%s" % (target, val)
        dataframes[key] = df[df[target] == val]

    return dataframes

# get (count + mp)/(total + m) from a dataframe for attrib
# takes the dataframe, the attribute, and the target attribute, returns dictionary
def attrib_count_m(df, attrib, target, m, p):
    total = len(df)
    counts = df[attrib].value_counts().to_dict()

    result = {}
    for key,c in counts.items():
        attribkey = "%s=%s|%s" % (attrib, key, target)
        result[attribkey] = (float(c) + float(p)*float(m))/(float(total) + float(m))
    # probably need this for later
    return result


# uses the attrib_count_m function to build a dictionary of probability 
# values for each potential attribute in the training data
def probability_counts(df, target, m, df_test):

    mp_dict = {}
    total = len(df)
    target_dfs = count_split(df, target)
    counts = {}
    for key,dfs in target_dfs.items():
        # this count is easy
        counts[key] = float(len(dfs))/float(total)

        # now do the counts of every column
        for col in dfs:

            # get the largest number in case one has zeroes
            total_attr = len(df_test[col].unique())
            if len(df[col].unique()) > len(df_test[col].unique()):
                total_attr = len(df[col].unique())

            p = 1.0/float(total_attr)
            dfs_counts = attrib_count_m(dfs, col, key, m, p)
            counts.update(dfs_counts)

            # make a separate dictionary for the p values
            mpkey = "%s|%s" %(col, key)
            #print mpkey
            mp_dict[mpkey] = p*m/float(len(dfs) + m)

    return counts, mp_dict


# turn counts into better data structure
def prediction_data_struct(counts):
    result = {}
    for key, item in counts.items():
        keys = key.split("|")
        if len(keys) > 1 and keys[0] == keys[1]:
            continue
        if len(keys) < 2 and keys[0] not in result:
            result[keys[0]] = {}
            result[keys[0]]['total'] = item
        elif len(keys) > 1 and keys[1] not in result:
            result[keys[1]] = {}
            result[keys[1]][keys[0]] = item
        elif len(keys) < 2 and keys[0] in result:
            result[keys[0]]['total'] = item
        elif len(keys) > 1 and keys[1] in result:
            result[keys[1]][keys[0]] = item
    return result


# math for testing data
def log_row(row, structure, mp_dict, m):
    results = {}
    # print row.to_dict()
    for k, s in structure.items():
        result = np.log10(structure[k]["total"])
        for attr in row.to_dict():


            mpkey = "%s|%s" % (attr, k)

            if attr in row.to_dict() and mpkey in mp_dict:
                key = "%s=%s" % (attr, row[attr])
                if key in structure[k]:
                    #print "%s %s" % (attr, np.log10(structure[k][key]))
                    result += np.log10(structure[k][key])
                else:
                    #print "%s zero: %s" % (attr, np.log10(mp_dict[mpkey]))
                    result += np.log10(mp_dict[mpkey])
        results[k] = result
    #print results
    best = highest_pred(results)
    label = best.split("=")
    return label[-1]

# highest of a standard dictionary of prediction values
def highest_pred(predict):
    vals = list(predict.values())
    keys = list(predict.keys())
    return keys[vals.index(max(vals))]

# find possible binary columns in the data
# returns a list of possible target attributes
def potentialTargets(df):
    targets = []
    for column in df:
        if len(df[column].value_counts().tolist()) != 0:
            targets.append(column)

    return targets

# test if data is compatible
def compat_data(df, tf, target):
    df_cols = df.columns
    tf_cols = tf.columns
    for col in df_cols:
        if col != target and col not in tf_cols:
            return False
    return True

if __name__ == "__main__":
    m = 1  
    
# print the prompts
    print ("\n-----------------------------------------------------")
    print ("\n\tAssignment 5: Naive Bayes Classifier Implementation")
    print ("\tJohna Latouf && Chaoran Zhou")
    print ("\n\tType 'quit' to exit or quit.")
    print ("\n-----------------------------------------------------")
    while True:
        # path: the data file name entered
        training_path = raw_input("\nPlease enter a training file (eg: data1): ")
        if training_path == "quit":
            sys.exit(0)
        try:
            open(training_path, 'r')
            break;
        except IOError:
            print("\nCan't open the file.")
            continue;
        except OSError:
            print("\nCan't open the file.")
            continue;
    #training file
    # booleans are weird, just make them strings
    boolReplace = {True: 'True', False: 'False'}
    df = read_data_file(training_path)  # read the file like a csv, put in dataframe
    df = df.replace(boolReplace)
    
    while True:
        # path: the data file name entered
        test_path = raw_input("\nPlease enter a testing file (eg: data2): ")
        if test_path == "quit":
            sys.exit(0)
        try:
            open(test_path, 'r')

            break;
        except IOError:
            print("\nCan't open the file.")
            continue;
        except OSError:
            print("\nCan't open the file.")
            continue;



            
    #test file 
    tf = read_data_file(test_path)  # read the file like a csv, put in dataframe    
    
    targets = potentialTargets(df)
    count = 1

    for t in targets:
        print "\t%s. %s" % (count, t)
        count += 1
            # path: the data file name entered

    while True:
        target_int = raw_input("\nPlease select the target attribute by number (eg. 1): ")
        if target_int == "quit":
            sys.exit(0)
        if target_int.isdigit() and int(target_int) <= len(targets) and int(target_int) > 0:
            break
        else:
            print "\nYou must select a valid digit"
            continue
    
    
    target = targets[int(target_int)-1]

    counts, mp_dict = probability_counts(df, target, m, tf)

    #print counts

    structure = prediction_data_struct(counts)

    #print structure

    # read a test data
    test_data = tf
    test_data = test_data.replace(boolReplace)

    # need to consider test data without target
    if target in test_data.columns:
        test_data_no_target = test_data.drop(target, axis=1)
        test_data['Classification'] = test_data_no_target.apply(lambda x: log_row(x, structure, mp_dict, m), axis=1)
    else:
        test_data_no_target = test_data
        test_data['Classification'] = test_data_no_target.apply(lambda x: log_row(x, structure, mp_dict, m), axis=1)

    # test_data['prediction'] = test_data_no_target.apply(lambda x: multiply_row(x, structure, mp_dict, m), axis=1)


    # get the accuracy
    if target in test_data.columns:
        accur = test_data[test_data["Classification"] == test_data[target]]
        accuracy = len(accur)
        acc_string = "\nAccuracy: %s/%s" % (accuracy, len(test_data))
    else:

        acc_string = "\nAccuracy: unknown"


    #print test_data


    result_file = open("Result.txt", "w")

    result_file.write(test_data.to_string())
    result_file.write(acc_string)
    
    result_file.close()
    
    print acc_string

    print ("\nThe result is in the file 'Result.txt'.")
    print ("\n********************Program End**********************")

