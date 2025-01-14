import glob
import os
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
from Tweet import Tweet
from Tweet_classified import Tweet_classified
from Crime import Crime
from datetime import datetime as dt
from datetime import timedelta

# Uncomment the processes you wish to undertake.
# to load raw tweets: load_tweets(tweet_path)
# to load classified tweets: load_final_classified_tweets(tweet_path)
# to convert to geojson: store_crimes_as_geojson(crimes, tweets) or store_crimes_as_geojson(crimes, tweets)

def main(tweet_path, crime_path):
    #tweets = load_tweets(tweet_path)
    #crimes = load_crime_data(crime_path)
    #tweets = load_final_classified_tweets(tweet_path)
    #print len(tweets)
    #store_crimes_as_geojson(crimes, tweets)
    #extract_hashtags(tweets)
    #tweet_timeseries = build_tweet_timeseries(tweets)
    #crime_timeseries = build_crime_timeseries(crimes)
    #plot_timeseries(tweet_timeseries,'Plot of Tweet timeseries')
    #grid_split_locations(tweets)
	pass

# This method outputs crime and tweet objects as geojson
# For use in the web app.
def store_crimes_as_geojson(crimes, tweets):
	myfile = open('output3.geojsonp', 'w')
	myfile.write("eqfeed_callback({\"type\":\"FeatureCollection\",\"features\":[\n")
	counter = 0;
	for crime in crimes:
		counter += 1
		if crime.crime_type and crime.latitude and crime.longitude:
			if counter == len(crimes):
				myfile.write("{\"type\":\"Feature\",\"properties\":{\"mytype\":\"crime\",\"description\":\"" + crime.crime_type + "\"},\"geometry\":{\"type\":\"Point\",\"coordinates\":["+ str(crime.latitude) + "," + str(crime.longitude) + "]},\"id\":\""+ str(counter) +"\"}\n")
			else:
				myfile.write("{\"type\":\"Feature\",\"properties\":{\"mytype\":\"crime\",\"description\":\"" + crime.crime_type + "\"},\"geometry\":{\"type\":\"Point\",\"coordinates\":["+ str(crime.latitude) + "," + str(crime.longitude) + "]},\"id\":\""+ str(counter) +"\"},\n")

	counter = 0;
	for tweet in tweets:
		counter += 1
		if tweet.classification and tweet.latitude and tweet.longitude and tweet.confidence:
			if counter == len(tweets):
				myfile.write("{\"type\":\"Feature\",\"properties\":{\"mytype\":\"tweet\",\"classification\":\"" + tweet.classification + "\",\"confidence\":\"" + tweet.confidence + "\"},\"geometry\":{\"type\":\"Point\",\"coordinates\":["+ str(tweet.latitude) + "," + str(tweet.longitude) + "]},\"id\":\""+ str(counter) +"\"}\n")
			else:
				myfile.write("{\"type\":\"Feature\",\"properties\":{\"mytype\":\"tweet\",\"classification\":\"" + tweet.classification + "\",\"confidence\":\"" + tweet.confidence + "\"},\"geometry\":{\"type\":\"Point\",\"coordinates\":["+ str(tweet.latitude) + "," + str(tweet.longitude) + "]},\"id\":\""+ str(counter) +"\"},\n")

	myfile.write("]});")
	myfile.close()

# loads in tweets that have been classified by the NLP process.
def load_final_classified_tweets(path):
	tweets = []
	with open(path, "rU") as data_file:
		reader = csv.reader(data_file, delimiter=',')
		counter = 0
		for entry in reader:
			if counter == 819:
				print 'here'
			counter += 1
			if len(entry) >= 8:
				tweet = Tweet_classified(entry[0], entry[1], entry[3], entry[7], entry[8])
				tweets.append(tweet)
			print counter
	return tweets

# Extracts hashtags from tweet objects and populates property: text_without_hashtags and hashtags
def extract_hashtags(tweets):
    for tweet in tweets:
        tweet.text_without_hashtags = tweet.text
        if '#' in tweet.text:
            tweet.hashtags = set([i[1:] for i in tweet.text.split() if i.startswith("#")])
            for hashtag in tweet.hashtags:
                tweet.text_without_hashtags = tweet.text_without_hashtags.replace('#' + hashtag, '')

#loads in crime data.
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

#loads in raw tweet data.
def load_tweets(path):
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
	tweet_ts = np.array(tweet_count_series)
	
	#---------------------Write Output for Excel Plots-----------
	np.savetxt('tweet_timeseries.csv',tweet_ts,delimiter=",",fmt=['%s','%1.3f'])
	return tweet_ts

if __name__ == "__main__":
    # Place the folder containing your twitter data as the first parameter (leave the r in)
    # Place the folder containing your police data as the second parameter (leave the r in)
    path = os.getcwd()
    twitter_path = path + '\\twitter_sample'
    crime_path = path + '\\Crime_sample'
    #main(twitter_path,crime_path)
    main(r"C:\Users\Ross\Downloads\Twitter", r"C:\Users\Ross\Dropbox\IRDMGROUP\Crime")
