from sqlite3.dbapi2 import Date
import sys
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, session, jsonify
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
import twint
import pandas as pd
from datetime import datetime
from datetime import date, timedelta
import datetime
import time
from inspect import getmembers
from pprint import pprint
import json

import re
from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer

#time for execution
import timeit
start_time = timeit.default_timer()

from nltk.corpus import sentiwordnet as swn
import random
import nltk
import re
from emoji import UNICODE_EMOJI
import emoji as emj
from nltk.stem.snowball import SnowballStemmer
import os
import math
import numpy as np
import nltk
nltk.download('stopwords') 
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
#from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
nltk.download('words')

from googletrans import Translator, constants

from vaderSentiment_fr.vaderSentiment import SentimentIntensityAnalyzer

from threading import Thread
import threading
import atexit
import Scrap as s
import Map as m
import time as t
import csv
import ReelCommentaire as rc


# variables that are accessible from anywhere
commonDataStruct = {}
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
yourThread = threading.Thread()

commonDataStruct["Statut"] = 0
# Session data
# statut_update
#   1 = en cours
#   0 = terminé

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_tweet(tweet_id):
    conn = get_db_connection()
    tweet = conn.execute('SELECT * FROM tweets WHERE id = ?',
                        (tweet_id,)).fetchone()
    conn.close()
    if tweet is None:
        abort(404)
    return tweet

def get_candidat(candidat_id):
    conn = get_db_connection()
    candidat = conn.execute('SELECT * FROM candidats WHERE id = ?',
                        (candidat_id,)).fetchone()
    conn.close()
    if candidat is None:
        abort(404)
    return candidat
    
#Check if a tweet is already in database
def is_already_in_db(tweet_id):
    conn = get_db_connection()
    res = conn.execute('SELECT * FROM tweets WHERE id = ?',
                        (tweet_id,)).fetchone()
    conn.close()
    if res:
        return True
    else:
        return False

#Check if a tweet text is already in database
def is_tweet_tex_already_in_db(tweet):
    conn = get_db_connection()
    res = conn.execute('SELECT * FROM tweets WHERE tweet = ?',
                        (tweet,)).fetchone()
    conn.close()
    if res:
        return True
    else:
        return False

def get_all_candidates():
    conn = get_db_connection()
    candidats = conn.execute('SELECT * FROM candidats').fetchall()
    conn.close()
    if candidats is None:
        abort(404)
    return candidats

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

@app.context_processor
def inject_update_state():
    return dict(update_state=commonDataStruct["Statut"])

@app.route('/')
def index():
    conn = get_db_connection()
    totalTweets = get_total_tweet()
    tweets = conn.execute('SELECT * FROM tweets').fetchall()
    candidats = conn.execute('SELECT * FROM candidats').fetchall()
    conn.close()
    last_tweets = get_last_tweets()
    global_feeling = get_global_feeling()
    today = date.today()
    get_logs()
    session['page'] = "twitter"
    #doStuffStart()
    return render_template('index.html',date=today,tweets=tweets, candidats=candidats, totalTweets=totalTweets, last_tweets=last_tweets, global_feeling=global_feeling)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/connexion',methods=['POST'])
def connexion():
    username = request.form.get('loginUsername')
    password = request.form.get('loginPassword')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?',(username,)).fetchone()
    conn.close()
    
    res = {}
    if user is None:
        res["code"] = 404
        res["message"] = "Compte inexistant"
        return res
    else :
        if not check_password_hash(user['password'], password):
            res["code"] = 500
            res["message"] = "Username ou Password incorrect"
            return res
        else:
            session['username'] = user['nom']
            session['statut_update'] = 0
            res["code"] = 200
            return res

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/<int:candidat_id>', methods=['GET'])
def candidat(candidat_id):
    candidat = get_candidat(candidat_id)
    last3_tweets = last_three_tweets(candidat_id)
    create_map(candidat_id)

    conn = get_db_connection()
    candidats = conn.execute('SELECT * FROM candidats').fetchall()
    conn.close()

    return render_template('candidat.html', candidat=candidat, last3_tweets=last3_tweets,candidats=candidats)

#@app.route('/create', methods=['GET'])
def create():
    res = {}
    count = 0
    conn = get_db_connection()
    all_candidats = get_all_candidates()
    try:
        for candidat in all_candidats:
            keywords = candidat['nom']
            getTweets(keywords,"file.csv")
            data = pd.read_csv("file.csv")
            #for tweet in data:
            #    print(tweet.timestamp,file=sys.stderr)
            for index, tweet in data.iterrows():
                tweet_t = tweet["tweet"]
                if tweet["language"] != "fr" :
                    translator = Translator()
                    tweet_t = translator.translate(tweet_t, dest="fr").text
                if is_already_in_db(tweet["id"]) != True and is_tweet_tex_already_in_db(tweet_t) != True:
                    tmp = tweet["created_at"].split()
                    date = tmp[0]+" "+tmp[1]
                    conn.execute('INSERT INTO tweets (tweet_id, tweet,username,created_at,candidat_id) VALUES (?,?,?,?,?)',(tweet["id"], tweet_t,tweet["username"],date,candidat['id']))
                    conn.commit()
                    count = count + 1
            os.remove("file.csv") 
        for candidat in all_candidats:
            id = candidat['id']
            ret = get_sentiments_score(id)
            if ret == 0:
                break
        add_vader_score()
        add_textblob_score()
    except sqlite3.Error :
        conn.rollback()
        res["code"] = 500
        res["message"] = "Une erreur s'est produite"
    
    conn.close()
    res["code"] = 200
    res["message"] = str(count)+"tweets ajoutés"
    
    return res

def get_total_tweet():
    conn = get_db_connection()
    tt_tweets = conn.execute("SELECT COUNT(*) as total, max(created_at) as last_date from tweets").fetchone()
    conn.close()

    return tt_tweets

def get_global_feeling():
    conn = get_db_connection()
    pos = conn.execute("SELECT COUNT(*) as positif from tweets where score_vader >= 0.05").fetchone()
    neg = conn.execute("SELECT COUNT(*) as negatif from tweets where score_vader <= -0.05").fetchone()
    neutre = conn.execute("SELECT COUNT(*) as neutre from tweets where score_vader < 0.05 and score_vader > -0.05").fetchone()
    conn.close()

    global_f = {}
    global_f["pos"] = pos["positif"]
    global_f["neg"] = neg["negatif"]
    global_f["neu"] = neutre["neutre"]
    global_f["total"] = pos["positif"] + neg["negatif"] + neutre["neutre"]

    return global_f

@app.route('/global_feeling', methods=['GET'])
def global_feeling():
    conn = get_db_connection()
    pos = conn.execute("SELECT COUNT(*) as positif from tweets where score_vader >= 0.05").fetchone()
    neg = conn.execute("SELECT COUNT(*) as negatif from tweets where score_vader <= -0.05").fetchone()
    neutre = conn.execute("SELECT COUNT(*) as neutre from tweets where score_vader < 0.05 and score_vader > -0.05").fetchone()
    conn.close()

    res = {}
    ps = pos["positif"]
    ng = neg["negatif"]
    ne = neutre["neutre"]
    total = ps + ng + ne
    res = jsonify({"pos":(100*ps)/total,"neg":(100*ng)/total,"neu":(100*ne)/total})

    return res

def getTweets(keywords,file):
    c = twint.Config()
    c.Search = keywords
    c.Custom["tweet"] = ["id","username", "tweet", "created_at","language"]
    c.Hide_output = True
    c.Limit = 1000
    c.Since = '2021-12-04'
    c.Until = '2021-12-05'
    c.Output = file
    c.Store_csv = True

    twint.run.Search(c)

def get_last_tweets():
    conn = get_db_connection()
    latest_tweets = conn.execute("SELECT id, username, tweet, created_at from tweets ORDER BY created_at DESC LIMIT 3").fetchall()
    conn.close()

    return latest_tweets

@app.route('/piechartdata', methods=['GET'])
def count_tweets_by_candidats():
    conn = get_db_connection()
    reparti_tweets = conn.execute("SELECT candidat_id, nom, count(tweet) as nb_tweets from tweets t INNER JOIN candidats c ON c.id=t.candidat_id  group by t.candidat_id;").fetchall()
    conn.close()
    
    piechartColors = ["#1abc9c","#e74c3c","#f1c40f","#2c3e50","#54a0ff","#01a3a4","#5352ed","#ff6b81","#6D214F","#BDC581","#6D214F","#FEA47F","#2c2c54"]
    
    data_color = []
    data_value = []
    candidat = []
    nb_tweets = []

    i = 0
    total = 0
    for row in reparti_tweets:
        data_color.append(piechartColors[i])
        total = total + row['nb_tweets']
        i = i+1
    for row in reparti_tweets:
        data_value.append(str((row['nb_tweets']*100)/total))
        nb_tweets.append(row['nb_tweets'])
        candidat.append(row['nom'])

    data_value = ','.join(data_value)
    piechart_data = jsonify({"color":data_color,"value":data_value,"candidat":{"nom":candidat,"nb_tweets":nb_tweets}})

    return piechart_data 

######## Add person #############
@app.route('/add_candidat/', methods=['GET'])
def compteexist():

    username = request.args.get('twitter')
    parti = request.args.get('parti')
    url_photo = request.args.get('photo')

    conn = get_db_connection()
    candidat = conn.execute('SELECT id FROM candidats WHERE twitter_username = ?',
                    (username,)).fetchone()
    conn.close()
    res = {}
    if candidat is None:
        c = twint.Config()
        c.Username = username
        c.Hide_output = True
        c.Store_object = True

        conn = get_db_connection()
        try:
            twint.run.Lookup(c)
            user = twint.output.users_list[0]

            conn = get_db_connection()
            conn.execute('INSERT INTO candidats (nom, parti_poli,twitter_username,count_tweets,count_following,count_followers,count_likes,url_photo) VALUES (?,?,?,?,?,?,?,?)',(user.name, parti,user.username,user.tweets,user.following,user.followers,user.likes,url_photo))
            conn.commit()

            doStuffStart()

            res["code"] = 200
            res["message"] = ""
        except Exception as e:
            conn.rollback()
            res["code"] = 500
            res["message"] = "Erreur lors du scrapping twitter"
            
    else:
        res["code"] = 0
        res["message"] = "compte déjà existant"
    
    conn.close()
    return res

######## Analyse des sentiments v1 
def get_tweets_for_one_candidat(candidat_id):
    conn = get_db_connection()
    tweets = conn.execute('SELECT tweet,tweet_id FROM tweets WHERE candidat_id = ?', (candidat_id,)).fetchall()
    conn.close()
    return tweets

def clean_tweet(text): 
    text = text.lower()
    text = text.replace('\n', ' ').replace('\r', '')
    text = ' '.join(text.split())
    text = re.sub(r"[A-Za-z\.]*[0-9]+[A-Za-z%°\.]*", "", text)
    text = re.sub(r"(\s\-\s|-$)", "", text)
    text = re.sub(r"[,\!\?\%\(\)\/\"]", "", text)
    text = re.sub(r"\&\S*\s", "", text)
    text = re.sub(r"\&", "", text)
    text = re.sub(r"\+", "", text)
    text = re.sub(r"\#", "", text)
    text = re.sub(r"\$", "", text)
    text = re.sub(r"\£", "", text)
    text = re.sub(r"\%", "", text)
    text = re.sub(r"\:", "", text)
    text = re.sub(r"\@", "", text)
    text = re.sub(r"\-", "", text) 

    return text

def get_tweet_sentiment(tweet):
    analysis = TextBlob(clean_tweet(tweet),pos_tagger=PatternTagger(),analyzer=PatternAnalyzer()).sentiment[0]   
    if analysis > 0: 
        return 'positif'
    elif analysis == 0: 
        return 'neutre'
    else: 
        return 'negatif'

@app.route('/feelings/<int:candidat_id>', methods=['GET'])
def get_saved_feelings(candidat_id):
    conn = get_db_connection()
    positif = conn.execute('SELECT COUNT(*) as positif FROM tweets WHERE candidat_id= ? AND score > 0',(candidat_id,)).fetchone()
    negatif = conn.execute('SELECT COUNT(*) as negatif FROM tweets WHERE candidat_id= ? AND score < 0',(candidat_id,)).fetchone()
    neutre = conn.execute('SELECT COUNT(*) as neutre FROM tweets WHERE candidat_id= ? AND score = 0',(candidat_id,)).fetchone()
    conn.close()

    p = round(100*positif['positif']/(positif['positif']+negatif['negatif']+neutre['neutre']))
    n = round(100*negatif['negatif']/(positif['positif']+negatif['negatif']+neutre['neutre']))
    neu = round(100 -(p+n))
    data_key = ["Positif","Negatif","Neutre"] 
    data_value = [p,n,neu] 

    data_dictionary = {"label": data_key,"data":data_value}
    json_data = json.dumps(data_dictionary, indent=4)
    
    return json_data

@app.route('/vader/<int:candidat_id>', methods=['GET'])
def get_vader_score(candidat_id):
    conn = get_db_connection()
    positif = conn.execute('SELECT COUNT(*) as positif FROM tweets WHERE candidat_id= ? AND score_vader >= 0.05',(candidat_id,)).fetchone()
    negatif = conn.execute('SELECT COUNT(*) as negatif FROM tweets WHERE candidat_id= ? AND score_vader <= -0.05',(candidat_id,)).fetchone()
    neutre = conn.execute('SELECT COUNT(*) as neutre FROM tweets WHERE candidat_id= ? AND score_vader < 0.5 AND score_vader > -0.5',(candidat_id,)).fetchone()
    conn.close()

    p = round(100*positif['positif']/(positif['positif']+negatif['negatif']+neutre['neutre']))
    n = round(100*negatif['negatif']/(positif['positif']+negatif['negatif']+neutre['neutre']))
    neu = round(100 -(p+n))
    data_key = ["Positif","Negatif","Neutre"] 
    data_value = [p,n,neu] 

    data_dictionary = {"label": data_key,"data":data_value}
    json_data = json.dumps(data_dictionary, indent=4)
    
    return json_data

@app.route('/TextBlob/<int:candidat_id>', methods=['GET'])
def get_TextBlob_score(candidat_id):
    conn = get_db_connection()
    positif = conn.execute('SELECT COUNT(*) as positif FROM tweets WHERE candidat_id= ? AND score_textblob > 0.0',(candidat_id,)).fetchone()
    negatif = conn.execute('SELECT COUNT(*) as negatif FROM tweets WHERE candidat_id= ? AND score_textblob < 0.0',(candidat_id,)).fetchone()
    neutre = conn.execute('SELECT COUNT(*) as neutre FROM tweets WHERE candidat_id= ? AND score_textblob = 0.0',(candidat_id,)).fetchone()
    conn.close()

    p = round(100*positif['positif']/(positif['positif']+negatif['negatif']+neutre['neutre']))
    n = round(100*negatif['negatif']/(positif['positif']+negatif['negatif']+neutre['neutre']))
    neu = round(100 -(p+n))
    data_key = ["Positif","Negatif","Neutre"] 
    data_value = [p,n,neu] 

    data_dictionary = {"label": data_key,"data":data_value}
    json_data = json.dumps(data_dictionary, indent=4)
    
    return json_data


def feelings_analysis_old(candidat_id):
    vals = get_tweets_for_one_candidat(candidat_id)
    all_tweets = []
    for row in vals:
        all_tweets.append(row['tweet'])
    tweets = []   
    for tweet in all_tweets: 
        parsed_tweet = {} 
        parsed_tweet['text'] = tweet
        parsed_tweet['sentiment'] = get_tweet_sentiment(tweet) 
        if parsed_tweet not in tweets: 
            tweets.append(parsed_tweet) 

    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positif'] 
    for p in ptweets:
        print(p,file=sys.stderr)
    #print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
    
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negatif'] 
    
    #print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
    #print("Neutral tweets percentage: {} %".format(100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets))) 
    
    data_key = ["Positif","Negatif","Neutre"]
    data_value = [100*len(ptweets)/len(tweets),100*len(ntweets)/len(tweets),100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets)]
    data_dictionary = {"label": data_key,"data":data_value}
    json_data = json.dumps(data_dictionary, indent=4)
    
    return json_data
    
    #print("\n\nPositive tweets:") 
    #for tweet in ptweets[:10]: 
    #    print(tweet['text']) 
  
    
    #print("\n\nNegative tweets:") 
    #for tweet in ntweets[:10]: 
    #    print(tweet['text'])
  
###### 3 last tweets for a candidat
def last_three_tweets(candidat_id):
    conn = get_db_connection()
    latest3_tweets = conn.execute('SELECT id, candidat_id, username, tweet, created_at, score_vader FROM tweets WHERE candidat_id = ? ORDER BY id DESC LIMIT 3', (candidat_id,)).fetchall()
    tweets_keys = ["id", "candidat_id", "username", "tweet", "created_at", "feeling"]
    tweets = []
    for row in latest3_tweets:
        print(row['score_vader'],file=sys.stderr)
        if row['score_vader'] >= 0.05:
            div = 1
        elif row['score_vader'] <= -0.5:
            div = 3
        else :
            div = 2

        vals = [row['id'],row['candidat_id'],row['username'],row['tweet'],row['created_at'],div]
        tweet = dict(zip(tweets_keys,vals))
        tweets.append(tweet)
    conn.close()
    return tweets

###### Analyse des sentiments v2
def get_sentiments_score(candidat_id):
    #------------------- files read ---------------------------------------
    pos = open('static/extras/positive-words-french.txt',"r",encoding='utf-8')
    neg = open('static/extras/negative-words-french.txt',"r",encoding='utf-8')
    brut_tweets = get_tweets_for_one_candidat(candidat_id)
    
    unclean_tweets = []
    for row in brut_tweets:
        unclean_tweets.append(row['tweet'])

    #------------------- nltk variables -----------------------------------

    words = list(set(w.lower() for w in nltk.corpus.words.words()))
    stopWords = list(set(w.lower() for w in nltk.corpus.stopwords.words('french')))

    stemmer = SnowballStemmer("french", ignore_stopwords=True)

    posTweets = []
    negTweets = []

    #------------------- variable declaration -----------------------------
    posWords = []
    negWords = []

    #------------------- file data to lists -------------------------------
    for line in pos:
        posWords.append(line.strip('\n').strip())

    for line in neg:
        negWords.append(line.strip('\n').strip())


    #-----------------recognize emojis------------------------------------------
    def is_emoji(s):
        count = 0
        for emoji in emj.UNICODE_EMOJI['fr']:
            count += s.count(emoji)
            if count > 1:
                return False
        return bool(count)

    #---------------extract emoji-------------------------------------------------
    def extract_emojis(s):
        return ''.join(c for c in s if c in emj.UNICODE_EMOJI['fr'])

    # - emoji sentiment rank from http://kt.ijs.si/data/Emoji_sentiment_ranking/ --
    emoji_SentimentScores = {}

    #happy, angry, love, sad, playful, confused
    emoji_SentimentScores["\xF0\x9F\x98\x82"] = 0.221 #0.221*2
    emoji_SentimentScores["\xF0\x9F\x98\xA1"] = -0.173 #-0.173
    emoji_SentimentScores["\xe2\x9d\xa4"] = 0.746 #0.746*2
    emoji_SentimentScores["\xF0\x9F\x98\xAD"] = -0.093 #-0.093*2
    emoji_SentimentScores["\xF0\x9F\x98\x9C"] = 0.445 #0.445*2
    emoji_SentimentScores["\xf0\x9f\x98\x95"] = -0.397 #0.397*2

    averageChangeInSentiment = sum(emoji_SentimentScores.values())/len(list(emoji_SentimentScores.values()))

    #--------- declare targets --------------------------

    targetEmoticons = {1: "happy", 2: "love", 3: "playful", 4: "sad", 5: "angry", 6: "confused"}

    #------------------------------ remove stopwords ---------------------------------------------------------------------

    tweets = []

    for row in unclean_tweets:
        row = ' '.join(re.sub("(@[A-Za-z0-9_]+)", "", row).split())

        #remove stopWords
        wordList = row.split()
        for word in wordList:
            if word in stopWords or len(word) == 1:
                if not is_emoji(word):
                    row = row.replace(" "+word+" ", " ")
                #print (word, row)
        try:
            tweets.append(row)
        except:
            pass

    #happy, love, playful, sad, angry, confused
    targets = [0]*len(tweets)

    for target in range(len(tweets)):
        if("\xF0\x9F\x98\x82" in tweets[target]):
            targets[target] = 1
        elif("\xF0\x9F\x98\xA1" in tweets[target]):
            targets[target] = 5
        elif("\xe2\x9d\xa4" in tweets[target]):
            targets[target] = 2
        elif("\xF0\x9F\x98\xAD" in tweets[target]):
            targets[target] = 4
        elif("\xF0\x9F\x98\x9C" in tweets[target]):
            targets[target] = 3
        elif("\xf0\x9f\x98\x95" in tweets[target]):
            targets[target] = 6


    #------- declare vars to store #, emojis, POS tags, sentiment Score for each tweet  ----

    hashtags = [""]*len(tweets)
    emojis = [""]*len(tweets)
    POStags = [""]*len(tweets)

    sentimentScore = [0]*len(tweets)
    sentiWord = [0] * len(tweets) #collector of sentiment Scores

    #--------------------------- assign #, emojis and store POS tags in POStags[] ------------------------------------

    idx = 0 #tweet counter

    for sentence in tweets:
        hashtags[idx] = []
        emojis[idx] = []

        splitSentence = sentence.split()

        for word in splitSentence:
            if "#" == word[0]:
                hashtags[idx].append(word)
            elif(is_emoji(word)):
                emoji_extracted = extract_emojis(word)
                emojis[idx].append(emoji_extracted)

        tweets[idx] = ' '.join(re.sub("(@[A-Za-z0-9_]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweets[idx]).split())
        sentence = ' '.join(re.sub("(@[A-Za-z0-9_]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", sentence).split())
        txt = nltk.word_tokenize(sentence)

        try:
            POStags[idx] = nltk.pos_tag(txt)
        except:
            pass
        idx += 1

    #------------------------------- get sentimentScore of emojis -------------------------------

    for i in range(len(emojis)):
        if(len(emojis[i]) == 0):
            pass
        else:
            #match sentiword with hashtag data
            for j in emojis[i]:
                if (j in list(emoji_SentimentScores.keys())):
                    sentimentScore[i] += emoji_SentimentScores[j]

    #------ logic to convert hashtags like ThisIsCamelCasing to [This, is, camel, casing] ------------

    def f1(w,c) : return list(zip(* [x_y for x_y in list(zip(w, list(range(len(w))))) if x_y[0] == c])[1])

    def getCamelCaseList(j):

        uppers = list(set([j.index(l) for l in j if l.isupper()]))

        indices = []

        for i in range(len(uppers)):
            indices.append(f1(j, j[uppers[i]]))

        indices.append([len(j)])

        indices = [item for sublist in indices for item in sublist]

        flat_list = []

        if (indices != []):
            for k in range(len(indices)-1):
                flat_list.append(str(j[indices[k]:indices[k + 1]]).lower())

        return  flat_list

    # #-------------------------------- get SentimentScore of hashtags ------------------------------

    for i in range(len(hashtags)):
        val = 0

        if (len(hashtags[i]) == 0):
            pass
        else:
            for hashWord in hashtags[i]:

                newj = tab = re.findall('[A-Z][^A-Z]*|[a-z][^A-Z]*', hashWord.lstrip('#'))

                if(newj != [] or hashWord!=""):
                    if(len(newj)>1):
                        for j in newj:
                            if j in posWords:
                                sentimentScore[i] += averageChangeInSentiment*2
                            elif j in negWords:
                                sentimentScore[i] -= averageChangeInSentiment*2
                else:
                    if hashWord in posWords:
                        sentimentScore[i] += averageChangeInSentiment*2
                    elif hashWord in negWords:
                        sentimentScore[i] -= averageChangeInSentiment*2

    # #---------------------------------- POS tagging -----------------------------

    class Splitter(object):
        def __init__(self):
            self.nltk_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
            self.nltk_tokenizer = nltk.tokenize.TreebankWordTokenizer()

        def split(self, text):

            sentences = self.nltk_splitter.tokenize(text)
            tokenized_sentences = [self.nltk_tokenizer.tokenize(sent) for sent in sentences]
            return tokenized_sentences

    class POSTagger(object):
        def __init__(self):
            pass

        def pos_tag(self, sentences):

            pos = [nltk.pos_tag(sentence) for sentence in sentences]
            pos = [[postag for (word, postag) in sentence] for sentence in pos] #(word, [postag])
            return pos

    for i in range(len(tweets)):

        splitter = Splitter()
        postagger = POSTagger()

        splitted_sentences = splitter.split(tweets[i])

        pos_tagged_sentences = postagger.pos_tag(splitted_sentences)

        for j in range(len(pos_tagged_sentences)):
            for k in range(len(pos_tagged_sentences[j])):
                #print pos_tagged_sentences[j][k], pos_tagged_sentences[j][k] in ['NN', 'NNS', 'NNP'], \
                    # pos_tagged_sentences[j][k] in ['JJ', 'JJR', 'JJS'], \
                    # pos_tagged_sentences[j][k] in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'], \
                    # splitted_sentences[j][k], splitted_sentences[j][k] in posWords, splitted_sentences[j][k] in negWords, \
                    # sentimentScore[i]

                try:
                    if(pos_tagged_sentences[j][k] in ['NN', 'NNS', 'NNP']):
                        if(splitted_sentences[j][k] in posWords):
                            if(k>0 and pos_tagged_sentences[j][k-1] in ['JJ', 'JJR', 'JJS']):
                                sentimentScore[i] += averageChangeInSentiment*2
                            else:
                                sentimentScore[i] += averageChangeInSentiment
                        elif(splitted_sentences[j][k] in negWords):
                            if(k>0 and pos_tagged_sentences[j][k-1] in ['JJ', 'JJR', 'JJS']):
                                sentimentScore[i] -= averageChangeInSentiment*2
                            else:
                                sentimentScore[i] -= averageChangeInSentiment
                    elif(pos_tagged_sentences[j][k] in ['JJ', 'JJR', 'JJS']):
                        if splitted_sentences[j][k] in posWords:
                            sentimentScore[i] += averageChangeInSentiment*2
                        elif splitted_sentences[j][k] in negWords:
                            sentimentScore[i] -= averageChangeInSentiment*2
                    elif(pos_tagged_sentences[j][k] in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']):
                        stemmed_verb = stemmer.stem(splitted_sentences[j][k])
                        if stemmed_verb in posWords:
                            sentimentScore[i] += averageChangeInSentiment*2
                        elif stemmed_verb in negWords:
                            sentimentScore[i] -= averageChangeInSentiment*2
                except:
                    pass
    i = 0
    conn = get_db_connection()
    for twt in brut_tweets :
        id = candidat_id
        t = twt['tweet_id']
        sc = sentimentScore[i]
        conn.execute('UPDATE tweets SET score = ?'
                         ' WHERE candidat_id = ? AND tweet_id = ? ',
                         (sc, id, t))
        i = i+1
        conn.commit()
    conn.close()

    #   for score in len(sentimentScore)):
    #       print(sentimentScore[score],file=sys.stderr)
    
    return 1

@app.route('/twitter/<string:words>', methods=['GET'])
def get_from_twitter(words):
    c = twint.Config()
    c.Search = words
    c.Custom["tweet"] = ["id", "username"]
    c.Limit = 1
    c.Lang = "fr"
    c.Hide_output = True
    c.Store_object = True
    c.Pandas = True

    twint.run.Search(c)
    tweets = twint.output.tweets_list
    str1 = json.dumps(tweets._dict_)
    return str1

def add_vader_score():
    conn = get_db_connection()
    tweets = conn.execute('SELECT * FROM tweets WHERE score_vader = -100').fetchall()
    conn.close()
    if tweets is None:
        return
    else:
        conn = get_db_connection()
        try:
            for tweet in tweets:
                # Create a SentimentIntensityAnalyzer object.
                analyzer = SentimentIntensityAnalyzer()

                # polarity_scores method of SentimentIntensityAnalyzer
                # object gives a sentiment dictionary.
                # which contains pos, neg, neu, and compound scores.
                sentiment_dict = analyzer.polarity_scores(tweet["tweet"])
                score = sentiment_dict['compound']
                #print("erreur insertion",file=sys.stderr)
                conn.execute('UPDATE tweets SET score_vader = ? WHERE id = ? ',(score, tweet["id"]))
                conn.commit()
        except sqlite3.Error :
            conn.rollback()
        conn.close()

def add_textblob_score():
    conn = get_db_connection()
    tweets = conn.execute('SELECT * FROM tweets WHERE score_textblob = -100').fetchall()
    conn.close()
    if tweets is None:
        return
    else:
        conn = get_db_connection()
        try:
            for tweet in tweets:
                score = TextBlob(tweet["tweet"],pos_tagger=PatternTagger(),analyzer=PatternAnalyzer()).sentiment[0]
                conn.execute('UPDATE tweets SET score_textblob = ? WHERE id = ? ',(score, tweet["id"]))
                conn.commit()
        except sqlite3.Error :
            conn.rollback()
        conn.close()

@app.route('/weekactivity/<int:candidat_id>', methods=['GET'])
def get_week_tweets(candidat_id):
    labels_day = []
    pos = []
    neg = []
    today = date.today()
    conn = get_db_connection()
                    
    for i in range(7):
        day = today - timedelta(days=i)
        day_french = day_in_french(day.strftime('%A'))
        labels_day.insert(0,day_french)
        day_iso_format = day.isoformat()
        day_iso_format = day_iso_format+"%" #symbole % pour utiliser LIKE val% en SQL 
        p = conn.execute('SELECT COUNT(*) AS total_p FROM tweets WHERE score_vader >= 0.05 AND created_at LIKE ? AND candidat_id = ? ',(day_iso_format,candidat_id)).fetchone()
        pos.insert(0,p["total_p"])
        n = conn.execute('SELECT COUNT(*) AS total_n FROM tweets WHERE score_vader <= -0.05 AND created_at LIKE ? AND candidat_id = ? ',(day_iso_format,candidat_id)).fetchone()
        neg.insert(0,n["total_n"])
        
    conn.close()
    data_dictionary = {"label": labels_day,"data_pos":pos,"data_neg":neg}
    json_data = json.dumps(data_dictionary, indent=4)
    #print(labels_day,file=sys.stderr)

    return json_data

@app.route('/globalweekactivity', methods=['GET'])
def get_global_week_tweets():
    labels_day = []
    nbr_tweets = []
    today = date.today()
    conn = get_db_connection()
                    
    for i in range(7):
        day = today - timedelta(days=i)
        day_french = day_in_french(day.strftime('%A'))
        labels_day.insert(0,day_french)
        day_iso_format = day.isoformat()
        day_iso_format = day_iso_format+"%" #symbole % pour utiliser LIKE val% en SQL 
        p = conn.execute('SELECT COUNT(*) AS total FROM tweets WHERE created_at LIKE ?',(day_iso_format,)).fetchone()
        nbr_tweets.insert(0,p["total"])
        
    conn.close()

    return jsonify({"label": labels_day,"nbr_tweets":nbr_tweets})

def day_in_french(day):
    if day == "Monday":
        return "Lundi"
    if day == "Tuesday":
        return "Mardi"
    if day == "Wednesday":
        return "Mercredi"
    if day == "Thursday":
        return "Jeudi"
    if day == "Friday":
        return "Vendredi"
    if day == "Saturday":
        return "Samedi"
    if day == "Sunday":
        return "Dimanche"

###################### get logs #####################
@app.route('/getlog', methods=['GET'])
def get_logs():
    
    data_date = []
    data_log = []
    data_t = {}
    if os.path.exists("static/extras/log.txt"):
        with open("static/extras/log.txt", 'r', encoding="UTF-8") as f:
            for line in f:
                x = line.split(",")
                data_date.append(x[0]) 
                data_log.append(x[1])
        data_t = jsonify({"date":data_date,"log":data_log})
    
    return data_t

def write_logs(message):
    now = datetime.datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H:%M:%S")

    if not os.path.exists("static/extras/log.txt"):
        file = open("static/extras/log.txt", "w")
        file.close() 

    with open('static/extras/log.txt', 'a', encoding="UTF-8") as f:
        f.write(dt_string+','+message)
        f.write('\n')
        f.close()

                #print(x[0],file=sys.stderr)

@app.route('/empty_logs')
def empty_logs():
    open('static/extras/log.txt', 'w').close()
    return jsonify({"code":200})

########## get 500 tweets by days on a week #########

def getTweetsByDay():
    all_candidats = get_all_candidates()
    for candidat in all_candidats:
        keywords = candidat['twitter_username']
        tab_tweets = s.update_tweets(900,keywords)
        print(candidat['twitter_username'],file=sys.stderr)
    return "ok"

def add_week_tweets_for_last_candidat_added():
    res = {}
    count = 0
    today = Date.today()
    conn = get_db_connection()
    #candidat_id = conn.execute('SELECT MAX(id) as id FROM candidats').fetchone()
    candidat_id = 3
    candidat = get_candidat(candidat_id)
    #candidat = get_candidat(candidat_id["id"])

    for i in range(7):
        c_day = today - timedelta(days=i)
        day_min = c_day.isoformat()
        n_day = today - timedelta(days=i+1)
        day_max = n_day.isoformat()

        print(day_min,file=sys.stderr)

        try:
            keywords = candidat["twitter_username"]
            getTweetsByDay(keywords,day_min,day_max,"file.csv")
            #while True:
            #    print("wait for file",file=sys.stderr)
            #    if os.path.exists("file.csv"):
            #        break
            data = pd.read_csv("file.csv")
            #for tweet in data:
            #    print(tweet.timestamp,file=sys.stderr)
            for index, tweet in data.iterrows():
                tweet_t = tweet["tweet"]
                if tweet["language"] != "fr" :
                    translator = Translator()
                    tweet_t = translator.translate(tweet_t, dest="fr").text
                if is_already_in_db(tweet["id"]) != True and is_tweet_tex_already_in_db(tweet_t) != True:
                    tmp = tweet["created_at"].split()
                    date = tmp[0]+" "+tmp[1]
                    conn.execute('INSERT INTO tweets (tweet_id, tweet,username,created_at,candidat_id) VALUES (?,?,?,?,?)',(tweet["id"], tweet_t,tweet["username"],date,candidat['id']))
                    conn.commit()
                    count = count + 1
            os.remove("file.csv") 
            #get_sentiments_score(candidat_id["id"])
            get_sentiments_score(candidat_id)
            add_vader_score()
            add_textblob_score()
        except sqlite3.Error :
            conn.rollback()
            res["code"] = 500
            res["message"] = "Une erreur s'est produite"
    
    conn.close()
    res["code"] = 200
    res["message"] = str(count)+"tweets ajoutés"

def add_week_tweets_for_all_candidat():
    res = {}
    count = 0
    today = Date.today()
    conn = get_db_connection()
    all_candidats = get_all_candidates()

    for candidat in all_candidats:
        for i in range(7):
            c_day = today - timedelta(days=i)
            day_min = c_day.isoformat()
            n_day = today - timedelta(days=i+1)
            day_max = n_day.isoformat()

            #print(day_min,file=sys.stderr)

            try:
                keywords = candidat["twitter_username"]
                getTweetsByDay(keywords,day_min,day_max,"file.csv")
                data = pd.read_csv("file.csv")
                #for tweet in data:
                #    print(tweet.timestamp,file=sys.stderr)
                for index, tweet in data.iterrows():
                    tweet_t = tweet["tweet"]
                    if tweet["language"] != "fr" :
                        translator = Translator()
                        tweet_t = translator.translate(tweet_t, dest="fr").text
                    if is_already_in_db(tweet["id"]) != True and is_tweet_tex_already_in_db(tweet_t) != True:
                        tmp = tweet["created_at"].split()
                        date = tmp[0]+" "+tmp[1]
                        conn.execute('INSERT INTO tweets (tweet_id, tweet,username,created_at,candidat_id) VALUES (?,?,?,?,?)',(tweet["id"], tweet_t,tweet["username"],date,candidat['id']))
                        conn.commit()
                        count = count + 1
                os.remove("file.csv") 
                get_sentiments_score(candidat["id"])
                add_vader_score()
                add_textblob_score()
            except sqlite3.Error :
                conn.rollback()
                res["code"] = 500
                res["message"] = "Une erreur s'est produite"
        
    conn.close()
    res["code"] = 200
    res["message"] = str(count)+"tweets ajoutés"

########### Intégration ############################

def add_tweets_v2():
    res = {}
    count = 0
    conn = get_db_connection()
    all_candidats = get_all_candidates()
    try:
        for candidat in all_candidats:
            keywords = candidat['twitter_username']
            tab_tweets = s.get_tweets(900,keywords)
            
            for tweet in tab_tweets:
                tweet_t = tweet[0]
                if is_already_in_db(tweet[3]) != True and is_tweet_tex_already_in_db(tweet_t) != True:
                    date = tweet[5].strftime("%Y-%m-%d %H:%M:%S")
                    conn.execute('INSERT INTO tweets (tweet_id, tweet,username,created_at,long,lat,candidat_id) VALUES (?,?,?,?,?,?,?)',(tweet[3], tweet_t,tweet[4],date,tweet[1],tweet[2],candidat['id']))
                    conn.commit()
                    count = count + 1
            message = str(count)+" tweets ajoutés"
            write_logs(message)
            count = 0

        message = "Calcul des scores"
        write_logs(message)
        """
        for candidat in all_candidats:
            id = candidat['id']
            ret = get_sentiments_score(id)
            if ret == 0:
                break
        
        message = "Fin calcul score algo"
        write_logs(message)
        """
        add_vader_score()

        message = "Fin calcul score vader"
        write_logs(message)

        add_textblob_score()

        message = "Fin calcul score textblob"
        write_logs(message)

    except sqlite3.Error :
        conn.rollback()
        res["code"] = 500
        res["message"] = "Erreur lors de l'ajout de tweets"
        write_logs(res["message"])
    
    conn.close()
    res["code"] = 200
    res["message"] = "Mise à jour terminée"
    write_logs(res["message"])
    
    return res

def get_tweets_with_coordonate(candidat_id):
    conn = get_db_connection()
    tweets = conn.execute('SELECT * FROM tweets WHERE long!=0.0 AND lat!=0.0 AND candidat_id = ? ',(candidat_id,)).fetchall()
    conn.close()
    if tweets is None:
        abort(404)
    return tweets

#@app.route('/create_map', methods=['GET'])
def create_map(candidat_id):
    Tweets_id=[]
    map,marker_cluster=m.create_map()
    tweets = get_tweets_with_coordonate(candidat_id)

    for tweet in tweets:
        Tweets_id.append(tweet["tweet_id"])
        m.add_Cluster_marker(marker_cluster,tweet["long"],tweet["lat"],bytes(tweet["tweet"], 'utf-8').decode(),tweet["score_vader"],tweet["username"],tweet["created_at"])
    map.render()
    m.save_map(map)
    return 'Map saved '+t.strftime("%H:%M:%S",  t.localtime())

@app.route('/youtube')
def youtube():
    session['page'] = "youtube"
    
    conn = get_db_connection()
    candidats = conn.execute('SELECT * FROM candidats').fetchall()
    candidat_data = conn.execute('SELECT y.id as vid_id, c.id as candidat_id, nom, score, avis_pos, avis_neg, nb_comments, emission, date_emission, id_video FROM youtube as y INNER JOIN candidats as c ON y.candidat_id=c.id').fetchall()
    conn.close()

    return render_template('youtube.html',candidat_data=candidat_data,candidats=candidats)


@app.route('/add_video/', methods=['GET'])
def add_video():

    id_youtube = request.args.get('id_youtube')
    emission = request.args.get('emission')
    candidat_id = request.args.get('candidat_id')
    data = rc.video_analyze(id_youtube,candidat_id,emission)
    date = data["date_emission"].replace('T',' ')
    date = date.replace('Z','')
    
    res = {}
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO youtube (score, avis_pos,avis_neg,nb_comments,candidat_id,emission,date_emission,id_video) VALUES (?,?,?,?,?,?,?,?)',(data["score"], data["avis_pos"],data["avis_neg"],data["nb_comments"],data["candidat_id"],data["emission"],date,data["id_video"]))
        conn.commit()
        res["code"] = 200
    except Exception as e:
        conn.rollback()
        res["code"] = 500
        res["message"] = "Erreur lors du scrapping twitter" 

    return res
    

    """
    conn = get_db_connection()
    candidat = conn.execute('SELECT id FROM candidats WHERE twitter_username = ?',
                    (username,)).fetchone()
    conn.close()
    
    if candidat is None:
        c = twint.Config()
        c.Username = username
        c.Hide_output = True
        c.Store_object = True

        conn = get_db_connection()
        try:
            twint.run.Lookup(c)
            user = twint.output.users_list[0]

            conn = get_db_connection()
            conn.execute('INSERT INTO candidats (nom, parti_poli,twitter_username,count_tweets,count_following,count_followers,count_likes,url_photo) VALUES (?,?,?,?,?,?,?,?)',(user.name, parti,user.username,user.tweets,user.following,user.followers,user.likes,url_photo))
            conn.commit()

            doStuffStart()

            res["code"] = 200
            res["message"] = ""
        except Exception as e:
            conn.rollback()
            res["code"] = 500
            res["message"] = "Erreur lors du scrapping twitter"          
    else:
        res["code"] = 0
        res["message"] = "compte déjà existant"
    
    conn.close()
    """
    return res


"""@app.route('/update_youtube')
def update_youtube():
    with open('sentiment_analysis.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        conn = get_db_connection()
        for row in spamreader:
            id_c = 0
            if row[0]== "Lepen":
                id_c = 3
            if row[0]== "Melenchon":
                id_c = 5
            if row[0]== "Valerie":
                id_c = 4
            if row[0]== "Zemmour":
                id_c = 1
            if id_c != 0:
                date = row[6].replace('T',' ')
                date = date.replace('Z','')
                conn.execute('INSERT INTO youtube (score, avis_pos,avis_neg,nb_comments,candidat_id,emission,date_emission,id_video) VALUES (?,?,?,?,?,?,?,?)',(row[1], row[2],row[3],row[4],id_c,row[5],date,100))
                conn.commit()
        conn.close()

    with open('data1.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        conn = get_db_connection()
        for row in spamreader:
            conn.execute('UPDATE youtube SET id_video = ? WHERE candidat_id = ? AND emission = ? ',(row[0], row[1], row[2]))
            conn.commit()
    return "ok"
    
"""

##########           threading      #################
@app.route("/test")
def test():
    doStuffStart()
    return jsonify({'thread_name': "update",
                    'started': True})

@app.route("/check_updateTweets_state")
def check_updateTweets_state():
    #session['statut_update'] = commonDataStruct["Statut"]
    return jsonify({'statut': commonDataStruct["Statut"]})

def function_called_by_thread():
    x = 150000
    for i in range(x):
        print("Working... {}/{}".format(i + 1, x))

def interrupt():
    global yourThread
    yourThread.cancel()

def doStuff():
    global commonDataStruct
    global yourThread
    commonDataStruct["Statut"] = 1
    with dataLock:
        add_tweets_v2()
        commonDataStruct["Statut"] = 0

def doStuffStart():
   # Do initialisation stuff here
    global yourThread
    # Create your thread
    yourThread = Thread(target=doStuff, args=())
    yourThread.setDaemon(True)
    yourThread.start()
    if os.path.exists("static/extras/log.txt"):
        os.remove("static/extras/log.txt")
    message = "thread update started"
    write_logs(message)

# When you kill Flask(SIGTERM), clear the trigger for the next thread
atexit.register(interrupt)


