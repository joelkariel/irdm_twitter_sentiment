import datetime

class Tweet:
    def __init__(self, country, date, latitude, longitude, placeName, placeType, profileLocation, text, tweetId,
                 username):
        self.country = country
        self.timestamp = datetime.datetime.fromtimestamp(int(date / 1000))
        self.date = datetime.datetime.fromtimestamp(int(date / 1000)).strftime('%d-%m-%Y')
        self.latitude = latitude
        self.longitude = longitude
        self.place_name = placeName
        self.place_type = placeType
        self.profile_location = profileLocation
        self.text = text
        self.text_without_hashtags = ''
        self.tweet_id = tweetId
        self.username = username
        self.hashtags = []
        self.classif = None
        self.conf = None
    def assign_sentiment(self,classification,confidence):
        '''Add and store sentiment of classified tweets '''
        self.classif = classification
        self.conf = confidence
    
