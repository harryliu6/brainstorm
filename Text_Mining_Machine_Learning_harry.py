"""
Mini Project 3
Text Mining Machine learning Study
Author: Chenlin (Harry) Liu
Date Created: 2020.3.7

"""
"""
In this part, I will use two labeled dataset with logistic regression or other methods 
to perform machine learning study on model training. The specific dataset is on racist wording and sentiment analysis in 
different input sentences. I got inspired by prateekjoshi565 in his research. (github) I hope I could profound my study in machine learning 
area, which I land my interest in. 

This program takes around 3-5 minutes to run and achieve the accuracy score of the model. 
Currently the public leaderboard for the score is 0.661
This program will achieve at around 0.6-0.63
"""
import re
from textblob import TextBlob
import pandas as pd

pd.set_option("display.max_colwidth", 200)
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import string
import nltk
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)
from nltk.corpus import stopwords
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import gensim
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

train = pd.read_csv('train_dataset.csv')
test = pd.read_csv('test_dataset.csv')  # Get the two dataset

# Preprocessing and Cleaning
# Print out the dimensions of each dataset
# print((train.shape, test.shape))

# Get how many are labeled racist or sexist (1) and how many are not (0)
# print(train['label'].value_counts())

# To do the data preprocessing, we would combine both train and test dataset to do it together
combined_dataset = train.append(test, ignore_index=True)  # Do not use the index labels to append


# Define a function to remove the patterns in the text
def remove_pattern(in_txt, pattern):
    r = re.findall(pattern, in_txt)  # use re.findall function to search for all patterns within the text
    for i in r:
        in_txt = re.sub(i, '', in_txt)  # use re.sub to substitute i in r with empty space
    return in_txt


# remove any @user in the tweet (or could use split() in my text_mining code)
combined_dataset['clean_tweet'] = np.vectorize(remove_pattern)(combined_dataset['tweet'], "@[\w]*")

# replace all the non_alphabet items with empty space
combined_dataset['clean_tweet'] = combined_dataset['clean_tweet'].str.replace("[^a-zA-Z#]", " ")

# use stopwords function to get rid of all common words to save computational power
combined_dataset['clean_tweet'] = combined_dataset['clean_tweet'].apply(
    lambda x: ' '.join([word for word in x.split() if word.lower() not in stopwords.words('english')]))


# print(combined_dataset['clean_tweet'].head()) check if all above is working correctly

# Try to visualize the words
def visual_word(all_data):
    wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_data)

    plt.figure(figsize=(10, 7))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()


good_words = ' '.join([word for word in combined_dataset['clean_tweet'][combined_dataset['label'] == 0]])
# visual_word(good_words) #Print out the good words

# Next we need to change words into vectors or extract features from tweets
# I choose to change words into vectors
# Store them as vectors and a much faster mapping process could be achieved by using vectors.

# Word2Vec Embeddings
split_tweet = combined_dataset['clean_tweet'].apply(lambda x: x.split())

# 200 independent variables (size) #change seed to see different results
mod_word2vec = gensim.models.Word2Vec(split_tweet, size=200, window=5, min_count=2, sg=1, hs=0, negative=10, workers=2,
                                      seed=64)

mod_word2vec.train(split_tweet, total_examples=len(combined_dataset['clean_tweet']), epochs=20)
mod_word2vec.wv.most_similar(positive='trump') #pull out the most similar words from the corpus

# Now we change every word into vectors
# print(mod_word2vec['trump'])

# Then we create a vector for each tweet using the average of the vectors of the words in the tweet
def word2vec_calc(split_word, size):
    vectors = np.zeros(size).reshape((1, size))
    cnt = 0
    for word in split_word:
        try:
            vectors = vectors + mod_word2vec[word].reshape((1,size)) #put all the reshaped word vectors into the vectors
            cnt = cnt + 1
        except KeyError:
            # print('Please change the word')
            continue
    if cnt != 0:
        vectors = vectors/cnt
    return vectors

word2vec_arrays = np.zeros((len(split_tweet),200))

for i in range(len(split_tweet)):
    word2vec_arrays[i,:] = word2vec_calc(split_tweet[i],200) #calculate the vectors for every word in the split tweet
    #and put them into the arrays

word2vec_dataset = pd.DataFrame(word2vec_arrays)
# print(word2vec_dataset.shape) #check if all words are captured and form (49159,200) dimension

# After turning the words into vectors, we could start to use models to do machine learning.
# Although we do the data preprocessing together for both training and test dataset, but we need to find out the dimensions
# of each before building models and testing models on each of them.

# I choose to use the logistic regression

train_word2vec = word2vec_dataset.iloc[:31962, :] #see dimensions of the training dataset at the beginning
test_word2vec = word2vec_dataset.iloc[31962:, :]

xtrain_word2vec, xvalid_word2vec, ytrain, yvalid = train_test_split(train_word2vec, train['label'], random_state=37, test_size=0.3)
#change random-state to see different randomized training and testing datasets

xtrain_word2vec = train_word2vec.iloc[ytrain.index, :]
xvalid_word2vec = train_word2vec.iloc[yvalid.index, :] #iloc is for purely integer-location based indexing for selection by position

lreg = LogisticRegression()
lreg.fit(xtrain_word2vec, ytrain)

prediction = lreg.predict_proba(xvalid_word2vec)
prediction_int = prediction[:, 1] >= 0.3 #learning rate of 0.3 is used
prediction_int = prediction_int.astype(np.int)
print(f1_score(yvalid, prediction_int))



