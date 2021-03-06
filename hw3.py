
from string import punctuation

import numpy as np

# !!! MAKE SURE TO USE SVC.decision_function(X), NOT SVC.predict(X) !!!
# (this makes ``continuous-valued'' predictions)
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold
from sklearn import metrics
import matplotlib.pyplot as plt

######################################################################
# functions -- input/output
######################################################################

def read_vector_file(fname):
    """
    Reads and returns a vector from a file.
    
    Parameters
    --------------------
        fname  -- string, filename
        
    Returns
    --------------------
        labels -- numpy array of shape (n,)
                    n is the number of non-blank lines in the text file
    """
    return np.genfromtxt(fname)


def write_label_answer(vec, outfile):
    """
    Writes your label vector to the given file.
    
    Parameters
    --------------------
        vec     -- numpy array of shape (n,) or (n,1), predicted scores
        outfile -- string, output filename
    """
    
    # for this project, you should predict 70 labels
    if(vec.shape[0] != 70):
        print("Error - output vector should have 70 rows.")
        print("Aborting write.")
        return
    
    np.savetxt(outfile, vec)    


######################################################################
# functions -- feature extraction
######################################################################

def extract_words(input_string):
    """
    Processes the input_string, separating it into "words" based on the presence
    of spaces, and separating punctuation marks into their own words.
    
    Parameters
    --------------------
        input_string -- string of characters
    
    Returns
    --------------------
        words        -- list of lowercase "words"
    """
    
    for c in punctuation :
        input_string = input_string.replace(c, ' ' + c + ' ')
    return input_string.lower().split()


def extract_dictionary(infile):
    """
    Given a filename, reads the text file and builds a dictionary of unique
    words/punctuations.
    
    Parameters
    --------------------
        infile    -- string, filename
    
    Returns
    --------------------
        word_list -- dictionary, (key, value) pairs are (word, index)
    """
    
    word_list = {}
    with open(infile, 'r') as fid :
        ### ========== TODO : START ========== ###
        # part 1a: process each line to populate word_list
        line = fid.readline()
        while line:
            l = extract_words(line)
            for s in l:
                word_list[s] = word_list.get(s,len(word_list))
            line = fid.readline()
        ### ========== TODO : END ========== ###

    print(len(word_list))
    return word_list

def extract_feature_vectors(infile, word_list):
    """
    Produces a bag-of-words representation of a text file specified by the
    filename infile based on the dictionary word_list.
    
    Parameters
    --------------------
        infile         -- string, filename
        word_list      -- dictionary, (key, value) pairs are (word, index)
    
    Returns
    --------------------
        feature_matrix -- numpy array of shape (n,d)
                          boolean (0,1) array indicating word presence in a string
                            n is the number of non-blank lines in the text file
                            d is the number of unique words in the text file
    """
    
    num_lines = sum(1 for line in open(infile,'r'))
    num_words = len(word_list)
    feature_matrix = np.zeros((num_lines, num_words))
    
    with open(infile, 'r') as fid :
        ### ========== TODO : START ========== ###
        # part 1b: process each line to populate feature_matrix
        for lc in range(0,num_lines):
            line = fid.readline()
            l = extract_words(line)
            for s in l:
                feature_matrix[lc][word_list[s]] = 1
        ### ========== TODO : END ========== ###
        
    return feature_matrix


######################################################################
# functions -- evaluation
######################################################################

def performance(y_true, y_pred, metric="accuracy"):
    """
    Calculates the performance metric based on the agreement between the 
    true labels and the predicted labels.
    
    Parameters
    --------------------
        y_true -- numpy array of shape (n,), known labels
        y_pred -- numpy array of shape (n,), (continuous-valued) predictions
        metric -- string, option used to select the performance measure
                  options: 'accuracy', 'f1-score', 'auroc', 'precision',
                           'sensitivity', 'specificity'        
    
    Returns
    --------------------
        score  -- float, performance score
    """
    # map continuous-valued predictions to binary labels
    y_label = np.sign(y_pred)
    y_label[y_label==0] = 1
    
    ### ========== TODO : START ========== ###
    # part 2a: compute classifier performance
    if metric == 'accuracy':
        return metrics.accuracy_score(y_true, y_label)
    elif metric == 'f1-score':
        return metrics.f1_score(y_true, y_label)
    elif metric == 'auroc':
        return metrics.roc_auc_score(y_true,y_pred)
    elif metric == 'precision':
        return metrics.precision_score(y_true, y_label)
    elif metric == 'sensitivity':
        m = metrics.confusion_matrix(y_true,y_label)
        if m[1][1]==0 and m[1][0]==0:
            return 0
        else:
            return m[1][1]/(m[1][0]+m[1][1])
    elif metric == 'specificity':
        m = metrics.confusion_matrix(y_true,y_label)
        if m[1][1]==0 and m[0][1]==0:
            return 0
        else:
            return m[1][1]/(m[1][1]+m[0][1])
    else:
        print('Unknown Metrics!!!!!')
        return 0
    ### ========== TODO : END ========== ###


def cv_performance(clf, X, y, kf, metric="accuracy"):
    """
    Splits the data, X and y, into k-folds and runs k-fold cross-validation.
    Trains classifier on k-1 folds and tests on the remaining fold.
    Calculates the k-fold cross-validation performance metric for classifier
    by averaging the performance across folds.
    
    Parameters
    --------------------
        clf    -- classifier (instance of SVC)
        X      -- numpy array of shape (n,d), feature vectors
                    n = number of examples
                    d = number of features
        y      -- numpy array of shape (n,), binary labels {1,-1}
        kf     -- cross_validation.KFold or cross_validation.StratifiedKFold
        metric -- string, option used to select performance measure
    
    Returns
    --------------------
        score   -- float, average cross-validation performance across k folds
    """
    
    ### ========== TODO : START ========== ###
    # part 2b: compute average cross-validation performance
    score = []
    for train,test in kf.split(X,y):
        X_train = X[train]
        X_test = X[test]
        y_train = y[train]
        y_test = y[test]
        clf.fit(X_train,y_train)
        y_pred = clf.decision_function(X_test)
        score.append(performance(y_test, y_pred, metric))
    
    score = np.array(score)
    return np.average(score)
    ### ========== TODO : END ========== ###


def select_param_linear(X, y, kf, metric="accuracy"):
    """
    Sweeps different settings for the hyperparameter of a linear-kernel SVM,
    calculating the k-fold CV performance for each setting, then selecting the
    hyperparameter that 'maximize' the average k-fold CV performance.
    
    Parameters
    --------------------
        X      -- numpy array of shape (n,d), feature vectors
                    n = number of examples
                    d = number of features
        y      -- numpy array of shape (n,), binary labels {1,-1}
        kf     -- cross_validation.KFold or cross_validation.StratifiedKFold
        metric -- string, option used to select performance measure
    
    Returns
    --------------------
        C -- float, optimal parameter value for linear-kernel SVM
    """
    
    print('Linear SVM Hyperparameter Selection based on ' + str(metric) + ':')
    C_range = 10.0 ** np.arange(-3, 3)
    
    ### ========== TODO : START ========== ###
    Res = []
    for c in C_range:
        svc = SVC(C=c, kernel='linear')
        res = cv_performance(svc, X, y, kf, metric)
        Res.append(res)
    # part 2c: select optimal hyperparameter using cross-validation
    
    plt.plot(np.arange(-3, 3),Res,label=metric)
    plt.legend()
    plt.show()
    maxc = 0
    for i in range(len(C_range)):
        if Res[i]>Res[maxc]:
            maxc = i
    print(str(C_range[maxc]) + ' and the ' + str(metric) + ' is: ' + str(Res[maxc]))
    return C_range[maxc]
    ### ========== TODO : END ========== ###


def select_param_rbf(X, y, kf, metric="accuracy"):
    """
    Sweeps different settings for the hyperparameters of an RBF-kernel SVM,
    calculating the k-fold CV performance for each setting, then selecting the
    hyperparameters that 'maximize' the average k-fold CV performance.
    
    Parameters
    --------------------
        X       -- numpy array of shape (n,d), feature vectors
                     n = number of examples
                     d = number of features
        y       -- numpy array of shape (n,), binary labels {1,-1}
        kf     -- cross_validation.KFold or cross_validation.StratifiedKFold
        metric  -- string, option used to select performance measure
    
    Returns
    --------------------
        gamma, C -- tuple of floats, optimal parameter values for an RBF-kernel SVM
    """
    
    print('RBF SVM Hyperparameter Selection based on ' + str(metric) + ':')
    
    ### ========== TODO : START ========== ###
    # part 3b: create grid, then select optimal hyperparameters using cross-validation
    C_range = 10.0 ** np.arange(-3, 3)
    g_range = 10.0 ** np.arange(-3, 3)
    
    maxc, maxg = 0, 0
    maxv = 0
    
    for c in C_range:
        for g in g_range:
            svc = SVC(C=c, gamma=g, kernel='rbf')
            res = cv_performance(svc, X, y, kf, metric)
            if res>maxv:
                maxc = c
                maxg = g
                maxv = res
    return maxc, maxg, maxv
    ### ========== TODO : END ========== ###


def performance_test(clf, X, y, metric="accuracy"):
    """
    Estimates the performance of the classifier using the 95% CI.
    
    Parameters
    --------------------
        clf          -- classifier (instance of SVC)
                          [already fit to data]
        X            -- numpy array of shape (n,d), feature vectors of test set
                          n = number of examples
                          d = number of features
        y            -- numpy array of shape (n,), binary labels {1,-1} of test set
        metric       -- string, option used to select performance measure
    
    Returns
    --------------------
        score        -- float, classifier performance
    """

    ### ========== TODO : START ========== ###
    # part 4b: return performance on test data by first computing predictions and then calling performance

    y_pred = clf.decision_function(X)
    score = performance(y, y_pred, metric)
    return score
    ### ========== TODO : END ========== ###


######################################################################
# main
######################################################################
 
def main() :
    np.random.seed(1234)
    
    # read the tweets and its labels   
    dictionary = extract_dictionary('../data/tweets.txt')
    X = extract_feature_vectors('../data/tweets.txt', dictionary)
    y = read_vector_file('../data/labels.txt')
    
    metric_list = ["accuracy", "f1-score", "auroc", "precision", "sensitivity", "specificity"]
    
    ### ========== TODO : START ========== ###
    # part 1c: split data into training (training + cross-validation) and testing set
    X_train = X[0:560]
    y_train = y[0:560]
    X_test = X[560:]
    y_test = y[560:]
    # part 2b: create stratified folds (5-fold CV)
    kf = StratifiedKFold(n_splits=5)
    # part 2d: for each metric, select optimal hyperparameter for linear-kernel SVM using CV
    '''
    c_acc = select_param_linear(X_train,y_train,kf, 'accuracy')
    c_f1 = select_param_linear(X_train,y_train,kf, 'f1-score')
    c_auroc = select_param_linear(X_train,y_train,kf, 'auroc')
    c_prec = select_param_linear(X_train,y_train,kf, 'precision')
    c_sensi = select_param_linear(X_train,y_train,kf, 'sensitivity')
    c_speci = select_param_linear(X_train,y_train,kf, 'specificity')
    '''
    # part 3c: for each metric, select optimal hyperparameter for RBF-SVM using CV
    '''
    print(select_param_rbf(X_train,y_train,kf, 'accuracy'))
    print(select_param_rbf(X_train,y_train,kf, 'f1-score'))
    print(select_param_rbf(X_train,y_train,kf, 'auroc'))
    print(select_param_rbf(X_train,y_train,kf, 'precision'))
    print(select_param_rbf(X_train,y_train,kf, 'sensitivity'))
    print(select_param_rbf(X_train,y_train,kf, 'specificity'))
    '''
    # part 4a: train linear- and RBF-kernel SVMs with selected hyperparameters
    svc1 = SVC(C=1.0, kernel='linear')
    svc2 = SVC(C=100, gamma=0.1, kernel='rbf')
    svc1.fit(X_train,y_train)
    svc2.fit(X_train,y_train)

    for metr in metric_list:
        print('\hline linear & '+metr+' & '+str(performance_test(svc1,X_test,y_test,metr))+' \\\\')
        print('\hline rbf & '+metr+' & '+str(performance_test(svc2,X_test,y_test,metr))+' \\\\')

    # part 4c: report performance on test data
    
    ### ========== TODO : END ========== ###
    
    
if __name__ == "__main__" :
    main()
