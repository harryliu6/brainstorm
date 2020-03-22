"""
Mini Project 3
Text Mining
Author: Chenlin (Harry) Liu
Date Created: 2020.2.29

"""
import twitter
import re
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import numpy as np
from nltk.corpus import stopwords
from nltk.stem.porter import *

twitter_api = twitter.Api(consumer_key='tFM0mKyAjLcvxP9XMIJ7VXCOt',
                          consumer_secret='cMb8pQdiNbTcowh0lb41CP5zKy0JWkzihsNVKpwh6DLMubcunE',
                          access_token_key='910916508787855360-PDtpxlj5s8vmIkGRBYr8Ub9gVEX900o',
                          access_token_secret='el2MGjnU4NuCP2dwDwjcqrmSVLxR5TfdibTTcyLRCFbzs')

print(twitter_api.VerifyCredentials())
# api.GetUserTimeline(screen_name='gvanrossum')

def get_key_dataset(keyword):
    try:
        tweets_test = twitter_api.GetSearch(keyword, count=50)
        return [{"test_text": i.text, "Mark": None} for i in tweets_test]
###Get the test_dataset in our analysis, return the text in a list of dictionaries with mark
###Mark will be further filled with positive/negative/neutral for sentiment analysis
    except:
        print('Not Good Keyword')
        return None

keyword = input("Please input your keyword: ")
key_data = get_key_dataset(keyword)

# key_data = [{
#                 'test_text': "When Shell invited me to come to London and advise the company's global warming response, I asked if there was an N… https://t.co/dayk21aJwm",
#                 'Mark': None}, {
#                 'test_text': 'Rainforests are losing their ability to absorb CO2, says a new study — because of climate change.\n\n🌳 They already a… https://t.co/qbacKsBvYv',
#                 'Mark': None}, {
#                 'test_text': 'does anyone else think global warming is a good thing? i like bernie. i think hes a really interesting artist.',
#                 'Mark': None}, {
#                 'test_text': 'RT @sachinjacobk: @mulindwa_guy @patriciakombo @UNFCCC @UNEP @unredd @JoinUN75 @unhabitatyouth @vanessa_vash @GretaThunberg @UNYouthEnvoy @…',
#                 'Mark': None}, {
#                 'test_text': "RT @saidruth: The country was literally on fire for months. We're going to bulldoze 3mn hectares of untouched forest in the next 15 years.…",
#                 'Mark': None}]

# print(key_data[0:5])  # test to see if it prints out first 5 items


# After getting the keyword dataset, I will clean the data I got and try to use nltk.sentimentanalyzer to
# analyze processed string.
# Then I could use the percentage of the positive or negative words to generate the sentiment regarding the
# keyword topic.

# Data preprocessing
def get_sentence(tweet):
    tweet_blob = TextBlob(tweet)
    return ' '.join(tweet_blob.words) #turn it into wrods without hashtags or @

print(get_sentence(key_data[0]['test_text']))

def no_user(tweet):
    tweet_list = [item for item in tweet.split() if item != 'user'] #search for item in the tweet.split(), add them in if it is not 'user'
    clean_item = [i for i in tweet_list if re.match(r'[^\W\d]*$', i)]
    clean_fin = ' '.join(clean_item)
    clean_end = [word for word in clean_fin.split() if word.lower() not in stopwords.words('english')]
    #use the stopword function in nltk to remove common words such as "is", "are" to save computational power
    # stem_1 = PorterStemmer()
    # clean_original = []
    # for word_end in clean_end:
    #     # stem_1.stem(word_end)
    #     clean_original.append(stem_1.stem(word_end))
    #
    # print(clean_original)
    #Decide not to use porterstemmer because it inaccurately turns words into non-words by removing their tense.
    #E.g: "invited" to "invit"; "advise" to "advis"
    clean_end_string = ' '.join(clean_end)
    return clean_end_string

processed_text = []
for i in range(0, len(key_data)):
    processed_text.append(no_user(get_sentence(key_data[i]['test_text'])))
print(processed_text)

all_results = []
for i in range(0, len(processed_text)):
    analyzer = SentimentIntensityAnalyzer()
    all_results.append(analyzer.polarity_scores(processed_text[i]))
print(all_results)

negative_cnt = 0
positive_cnt = 0
for i in range(0, len(all_results)):
    if all_results[i]['neg'] > all_results[i]['pos']:
        negative_cnt += 1
    if all_results[i]['pos'] >= all_results[i]['neg']:
        positive_cnt += 1
neg_sentiment_overall = negative_cnt/(negative_cnt+positive_cnt)
pos_sentiment_overall = positive_cnt/(negative_cnt+positive_cnt)
print("Negative sentiment is {} and positive sentiment is {}".format(neg_sentiment_overall,pos_sentiment_overall))



