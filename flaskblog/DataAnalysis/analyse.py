import csv
import tweepy
from flaskblog.DataAnalysis import extractData
from flaskblog.DataExtraction import input_key_date
from flaskblog.FileLocations import file_locations


class Analyse:

    def __init__(self):
        pass

    def analysis(self, api, hashtag, fromdate, d1, csvwriter):
        for tweet in tweepy.Cursor(api.search, q="#" + hashtag,
                                   lang="en",
                                   since=fromdate).items():
            d2 = tweet.created_at
            if d2 <= d1:
                print(".", end = " ")
                csvwriter.writerow(
                    [tweet.created_at, tweet.text.encode('utf-8'), tweet.user.screen_name.encode('utf-8'),
                     tweet.favorite_count, tweet.retweet_count, tweet.coordinates])


if __name__ == '__main__':

    extract_data = extractData.ExtractData()
    analyse_data = Analyse()
    inputs = input_key_date.TakeInput()
    hashtag = inputs.hashtag()
    b = input("Do you want to enter date constraint? Y/N? ")
    from_date = inputs.from_date(b)
    to_date = inputs.to_date(b)
    csvFile = open(file_locations.dataset, 'w')
    csvWriter = csv.writer(csvFile)
    analyse_data.analysis(extract_data.authorize(), hashtag, from_date, to_date, csvWriter)
