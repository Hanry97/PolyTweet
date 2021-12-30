import re
from sqlite3.dbapi2 import Date
import sys
import snscrape.modules.twitter as sntwitter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from geopy.geocoders import Nominatim
from datetime import date, datetime, timedelta

def get_tweets(N,username):
    geolocator = Nominatim(user_agent="geoapiExercises")
    analyser = SentimentIntensityAnalyzer()
    tab=[]
    cpt=0
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(username).get_items()):
        if i > N:
            
            break
        tweet.content = re.sub(r"\.","",tweet.content)
        #print(tweet.place,file=sys.stderr)
        coord=False
        if tweet.place is not None:
            if tweet.coordinates is not None:
                coord=True
                address='?'
            else:
                coord=False
                address=tweet.place
                location = geolocator.geocode(address)
                
            if coord==True : 
                tab.append([tweet.content,tweet.coordinates.longitude,tweet.coordinates.latitude,tweet.id,tweet.user.username,tweet.date])
            else:
                print(location.latitude,location.longitude)
                tab.append([tweet.content,location.longitude,location.latitude,tweet.id,tweet.user.username,tweet.date])
        else:
            tab.append([tweet.content,0.0,0.0,tweet.id,tweet.user.username,tweet.date])

    return tab

def get_utilisateur_plus_date(id):
    geolocator = Nominatim(user_agent="geoapiExercises")
    analyser = SentimentIntensityAnalyzer()
    tab=[]
    
    for i,tweet in enumerate(sntwitter.TwitterTweetScraper(id,sntwitter.TwitterTweetScraperMode.SINGLE).get_items()):
        coord = False
        if tweet.place is not None:
            if tweet.coordinates is not None:
                coord=True
                address='?'
                coord = True
            else:
                coord=False
                address=tweet.place
                location = geolocator.geocode(address)

        score = analyser.polarity_scores(tweet.content)
        if coord==True : 
            tab.append([tweet.content,tweet.coordinates.longitude,tweet.coordinates.latitude,score,tweet.id,address,tweet.user.username,tweet.date.strftime("%D")])
        else :
            tab.append([tweet.content,tweet.coordinates.longitude,tweet.coordinates.latitude,score,tweet.id,address,tweet.user.username,tweet.date.strftime("%D")])
    return tab[0]


def update_tweets(N,username):
    geolocator = Nominatim(user_agent="geoapiExercises")
    analyser = SentimentIntensityAnalyzer()
    tab=[]
    cpt=0

    today = Date.today()
    for i in range(7):
        c_day = today - timedelta(days=i)
        day_min = c_day.isoformat()
        n_day = today - timedelta(days=i+1)
        day_max = n_day.isoformat()
        
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(username).get_items()):
            date_m = day_max+" 00:00:00"
            date_max = datetime.strptime(date_m, '%Y-%m-%d %H:%M:%S')

            date_mi = day_min+" 00:00:00"
            date_min = datetime.strptime(date_mi, '%Y-%m-%d %H:%M:%S')
            date_t = tweet.date
            date_t = date_t.replace(tzinfo=None)
            
            if i > N and date_t<date_max and date_t > date_min:
                
                break
            tweet.content = re.sub(r"\.","",tweet.content)
            #print(tweet.place,file=sys.stderr)
            coord=False
            if tweet.place is not None:
                if tweet.coordinates is not None:
                    coord=True
                    address='?'
                else:
                    coord=False
                    address=tweet.place
                    location = geolocator.geocode(address)
                    
                if coord==True : 
                    tab.append([tweet.content,tweet.coordinates.longitude,tweet.coordinates.latitude,tweet.id,tweet.user.username,tweet.date])
                else:
                    print(location.latitude,location.longitude)
                    tab.append([tweet.content,location.longitude,location.latitude,tweet.id,tweet.user.username,tweet.date])
            else:
                tab.append([tweet.content,0.0,0.0,tweet.id,tweet.user.username,tweet.date])

    return tab
