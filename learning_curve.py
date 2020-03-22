"""Explore learning curves for classification of handwritten digits"""

"""Header: 
   Author Name: Chenlin (Harry) Liu
   Date Created: 2020.2.27
   
"""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import *
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
# from sklearn.cross_validation import train_test_split


def display_digits():
    """Read in the 8x8 pictures of numbers and display 10 of them."""
    digits = load_digits()
    print(digits.DESCR)
    fig = plt.figure()
    for i in range(10):
        subplot = fig.add_subplot(5, 2, i + 1)
        subplot.matshow(np.reshape(digits.data[i], (8, 8)), cmap='gray')

    plt.show()

# def calc_acc(scores):
#     scores = np.array(scores)
#     return np.mean(scores, axis=1)

def train_model():
    """Train a model on pictures of digits.

    Read in 8x8 pictures of numbers and evaluate the accuracy of the model
    when different percentages of the data are used as training data. This
    y_size plots the average accuracy of the model as a function of the percent
    of data used to train it.
    """
    data = load_digits()
    num_trials = 10
    train_percentages = range(5, 95, 5)
    train_acc_all = []
    test_acc_all = []
    train_acc = []
    test_acc = []
    for percent in train_percentages:
        for trial in range(num_trials):
            X_train, X_test, y_train, y_test = train_test_split(data.data, data.target,
                                                                train_size=percent / 100)
            model = LogisticRegression()
            model.fit(X_train, y_train)
            train_acc.append(model.score(X_train, y_train))
            test_acc.append(model.score(X_test, y_test))

        train_acc_avg = sum(train_acc)/len(train_acc)
        test_acc_avg = sum(test_acc)/len(test_acc)
        train_acc_all.append(train_acc_avg)
        test_acc_all.append(test_acc_avg)
        print(test_acc_all)

    # train_acc_all, test_acc_all = calc_acc(train_acc_all), calc_acc(
    #     test_acc_all)  # use numpy array to generate means for all of the different percentage lists within.

    fig = plt.figure()
    plt.plot(train_percentages, test_acc_all)
    plt.xlabel("Percentage of Data Used for Training")
    plt.ylabel("Accuracy on Test Set")
    plt.show()


if __name__ == "__main__":
    # Feel free to comment/uncomment as needed
    display_digits()
    train_model()
