import glob
import os
import json
import csv
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math

from Tweet import Tweet
from Crime import Crime
from datetime import datetime as dt
from datetime import timedelta


def main(classified_tweet_path, crime_path):
    tweets = load_classified_tweets(classified_tweet_path)
    #crimes = load_crime_data(crime_path)
    #extract_hashtags(tweets)
    tweet_timeseries = build_tweet_timeseries(tweets)
    #crime_timeseries = build_crime_timeseries(crimes)
    #plot_timeseries(tweet_timeseries,'Plot of Tweet timeseries')
    grid_split_locations(tweets)
    
def extract_hashtags(tweets):
    for tweet in tweets:
        tweet.text_without_hashtags = tweet.text
        if '#' in tweet.text:
            tweet.hashtags = set([i[1:] for i in tweet.text.split() if i.startswith("#")])
            for hashtag in tweet.hashtags:
                tweet.text_without_hashtags = tweet.text_without_hashtags.replace('#' + hashtag, '')


def load_crime_data(path):
    crimes = []
    counter = 0

    for root, dirs, files in os.walk(path):
        for file in files:
            print root, file
            with open(os.path.join(root, file), "r") as data_file:
                reader = csv.reader(data_file, delimiter=',')
                next(reader, None)
                for entry in reader:
                    crime = Crime(entry[0], entry[1], entry[2], entry[3],
                              entry[4], entry[5], entry[6], entry[7],
                              entry[8], entry[9], entry[10], entry[11])
                    crimes.append(crime)
    return crimes


def load_classified_tweets(path):
    tweets = []
    num_files = len(glob.glob1(path, "*.txt"));
    counter = 0
    for filename in glob.glob(os.path.join(path, '*.txt')):
        if counter % 250 == 0:
            print "Parsing file: " + str(counter) + "/" + str(num_files)

        counter += 1
        with open(os.path.join(path, filename)) as data_file:
            data = json.load(data_file)["tweets"]
            for entry in data:
                tweet = Tweet(entry["country"], entry["date"], entry["latitude"], entry["longitude"],
                              entry["placeName"], entry["placeType"], entry["profileLocation"], entry["text"],
                              entry["tweetId"], entry["username"])
                tweets.append(tweet)
    print "Parsing complete"
    return tweets    
    

def plot_timeseries(ts,title):
	dates  = ts[:,0]
	values = ts[:,1]
	fig, ax = plt.subplots()
	ax.set_title(title)
	ax.set_xlabel('Day')
	ax.set_ylabel('Tweets')
	ax.plot(dates,values)

	plt.gcf().autofmt_xdate()
	#show graph
	plt.show()
	
	

def build_tweet_timeseries(tweets):
	
	#Get day range of dataset
	current_max = tweets[0].timestamp
	current_min = tweets[0].timestamp
	for tweet in tweets:
		if tweet.timestamp > current_max:
			current_max = tweet.timestamp
		if tweet.timestamp < current_min:
			current_min = tweet.timestamp
	first_date = current_min.date()
	last_date = current_max.date()
	print 'First: ', first_date, ' Last: ', last_date
	time_window = (last_date- first_date).days
	tweet_count_series = []
	# Count number of tweets on each day
	for d in range(0,time_window+1):
		curr_day = first_date + timedelta(days=d)
		tweet_count = 0
		# Count number of tweets if date matches current day
		tweet_count = sum(1 if tweet.timestamp.date() == curr_day else 0 for tweet in tweets)
		tweet_count_series.append([curr_day,tweet_count])
		print 'Day:',d,'of',time_window
		sys.stdout.flush()
	tweet_ts = np.array(tweet_count_series)
	
	#---------------------Write Output for Excel Plots-----------
	np.savetxt('tweet_timeseries.csv',tweet_ts,delimiter=",",fmt=['%s','%1.3f'])
	return tweet_ts

def build_crime_timeseries(crimes):
	print crimes[0].month


def grid_split_locations(tweets):
	''' Split the tweet data set by grid partition based on geolocations attached'''
	
	# 1) Get min/max of grid
	min_lat  = float('inf')
	max_lat  = -float('inf')
	min_long = float('inf')
	max_long = -float('inf')
	for tweet in tweets:
		if tweet.latitude  < min_lat:
			min_lat  = tweet.latitude
		if tweet.latitude  > max_lat:
			max_lat  = tweet.latitude
		if tweet.longitude < min_long:
			min_long = tweet.longitude
		if tweet.longitude > max_long:
			max_long = tweet.longitude 
	
	print 'Map ranges: ',int(min_lat),int(min_long),int(max_lat),int(max_long)
	# 2) Choose number of splits of grid and find quadrant coordinates
	n_split = 4
	lat_step  = (max_lat  - min_lat) /n_split 
	long_step = (max_long - min_long)/n_split
	
	quadrant_list = np.zeros((n_split*n_split,4))
	counter = 0
	for x in range(n_split):
		for y in range(n_split):
			# Format [lower-lat, upper-lat, lower-long,upper-long]
			quadrant = [(min_lat + x*lat_step), (min_lat + (x+1)*lat_step),
						(min_long+ y*long_step),(min_long+ (y+1)*long_step)]
			
			quadrant_list[counter,:] = quadrant
			counter += 1
      
	print quadrant_list

	# 3) Allocate tweet to quadrant
	quadrant_tweet_count = np.zeros((n_split*n_split,1))
	
	for tweet in tweets:
		quad = quadrant_allocate(quadrant_list,tweet.longitude,tweet.latitude)
		quadrant_tweet_count[quad] += 1
	print quadrant_tweet_count

def quadrant_allocate(quadrant_list,longitude, latitude):
    '''For a given long/lat pair determines which quadrant it belongs to'''
    #quadrant list in format [a (lat),b (lat),c (long),d (long)]
    curr_quad = 0
    for quad in quadrant_list:
        #if within latitude range
        if latitude >= quad[0] and  latitude <= quad[1]:
            if longitude >=quad[2] and  longitude <= quad[3]:
                return curr_quad
        curr_quad += 1
        
if __name__ == "__main__":
    # Place the folder containing your twitter data as the first parameter (leave the r in)
    # Place the folder containing your police data as the second parameter (leave the r in)
    path = os.getcwd()
    twitter_path = path + '\\twitter_sample'
    crime_path = path + '\\Crime_sample'
    main(twitter_path,crime_path)
    #main(r"C:\Users\Ross\Downloads\Twitter", r"C:\Users\Ross\Dropbox\IRDMGROUP\Crime")