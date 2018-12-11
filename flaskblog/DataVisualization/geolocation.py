import tweepy
import gmplot
import re
import pandas as pd
from flaskblog.FileLocations import file_locations
from flaskblog.DataAnalysis import extractData
from flaskblog.DataExtraction import input_key_date


class Geo:

    def __init__(self):
        self.lat = []
        self.lon = []
        self.coordinates = []
        pass

    def extract_lat_lon(self, api, hashtag):
        for tweet in tweepy.Cursor(api.search, q="#" + hashtag,
                                   lang="en",
                                   since="").items():
            if str(tweet.coordinates).__contains__("coordinates"):
                print(".", end=" ")
                self.coordinates.append(str(tweet.coordinates))

    def plot_gmap(self, df):
        coordinates = df['coordinates']
        d = []
        for s in coordinates:
            if str(s) != "nan":
                d.append("" + re.findall('\[(.*)\]', str(s))[0])
        for y in d:
            self.lat.append(float(y.split(", ")[0]))
            self.lon.append(float(y.split(", ")[1]))
        gmap = gmplot.GoogleMapPlotter(0, 0, 1, apikey='AIzaSyDCl26E05vIT8hw7KMRjbghrlOLty7yIGo')
        gmap.heatmap(self.lat, self.lon)
        gmap.draw(file_locations.maps)


if __name__ == '__main__':
    extract_data = extractData.ExtractData()
    analyse_data = Geo()
    df = pd.read_csv(file_locations.dataset, names=['created_at', 'tweets', 'username', 'likes',
                                                    'retweet', 'coordinates'])
    # inputs = input_key_date.TakeInput()
    # hashtag = inputs.hashtag()
    # analyse_data.extract_lat_lon(extract_data.authorize(), hashtag)
    analyse_data.plot_gmap(df)
