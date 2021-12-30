#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 14:53:09 2021

Made in Marseille

@author: Théo PASQUIER et (un peu) Loïc Carron 
"""

import csv 
import numpy as np
import matplotlib.pyplot as plt
import math
from googleapiclient.discovery import build
from vaderSentiment_fr.vaderSentiment import SentimentIntensityAnalyzer

key='AIzaSyDsvB630E5Sf1dAjw44PvqKcrV7ecA4iEM'


class video:
    videoId=''
    CandidatName=''
    EmissionName=''
    date=''
    def __init__(self, videoId,CandidatName,EmissionName,date):
        self.videoId = videoId
        self.CandidatName = CandidatName
        self.EmissionName = EmissionName
        self.date = date

def video_comments(video):
    
    replies = [] 
    
    df=[]
    
    youtube = build('youtube', 'v3', 
                    developerKey=key) 
  
    
    video_response=youtube.commentThreads().list(
    textFormat='plainText',
    part='snippet',
    order='time',
    videoId=video.videoId ,maxResults=100
    ).execute() 
  
    video_detail=youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video.videoId
    ).execute()
    video.date=video_detail.get("items")[0]['snippet']['publishedAt']
    while video_response: 
        
        #print(video.date)
        
        for item in video_response['items']: 
            
            
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            #translated = GoogleTranslator(source='auto', target='en').translate(comment)
            df.append(comment)
  
        
        if 'nextPageToken' in video_response: 
            video_response=youtube.commentThreads().list(
            textFormat='plainText',
            part='snippet',
            order='time',
            pageToken = video_response['nextPageToken'],
            videoId=video.videoId , maxResults=100
            ).execute()
        else: 
            break
    return df

def youtube_analyze(self):
    mVideos=[]

    key='AIzaSyDsvB630E5Sf1dAjw44PvqKcrV7ecA4iEM'
    with open('data1.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:
            #print(row)
            mVideos.append(self.video(row[0],row[1],row[2],''))


    
    with open('sentiment_analysis.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Candidat'] +  ['Score'] + ['Avis_negatifs'] + ['Avis_Positifs'] + ['Nb_de_commentaires'] + ['Emission'] +['Date'])

        for video in mVideos:
            text=video_comments(video);
            analyzer = SentimentIntensityAnalyzer();
            moyenne=0;
            diviseur=0;
            nb_neg=0;
            nb_pos=0;
            Candidat_evol = []
            for sentence in text:
                vs = analyzer.polarity_scores(sentence)
                #print("{:-<65} {}".format(sentence, str(vs)))
                compound=vs['compound']
                if(compound<0):
                    nb_neg+=1;
                elif(compound>0):
                    nb_pos+=1;
                    moyenne+=compound;
                diviseur+=1;
            spamwriter.writerow([video.CandidatName] + [moyenne/diviseur] + [nb_neg/diviseur] + [nb_pos/diviseur] + [diviseur] + [video.EmissionName]+[video.date])
        

def video_analyze(videoId,candidat_id,emission):
    vid = video(videoId,candidat_id,emission,'')
    text=video_comments(vid);
    analyzer = SentimentIntensityAnalyzer();
    moyenne=0;
    diviseur=0;
    nb_neg=0;
    nb_pos=0;
    Candidat_evol = []
    for sentence in text:
        vs = analyzer.polarity_scores(sentence)
        #print("{:-<65} {}".format(sentence, str(vs)))
        compound=vs['compound']
        if(compound<0):
            nb_neg+=1;
        elif(compound>0):
            nb_pos+=1;
            moyenne+=compound;
        diviseur+=1;
    res = {}
    res["candidat_id"] = candidat_id
    res["score"] = moyenne/diviseur
    res["avis_neg"] = nb_neg/diviseur
    res["avis_pos"] = nb_pos/diviseur
    res["nb_comments"] = diviseur
    res["emission"] = emission
    res["date_emission"] = vid.date
    res["id_video"] = videoId
    #spamwriter.writerow([video.CandidatName] + [moyenne/diviseur] + [nb_neg/diviseur] + [nb_pos/diviseur] + [diviseur] + [video.EmissionName]+[video.date])
    
    return res
