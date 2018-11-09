import extractData
import csv
import sys
import tweepy
import input_key_date
sys.path.append("../DataExtraction/")


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
                    [tweet.created_at, tweet.text.encode('utf-8'), tweet.user.screen_name.encode('utf-8')])


if __name__ == '__main__':

    extract_data = extractData.ExtractData()
    analyse_data = Analyse()
    inputs = input_key_date.TakeInput()
    hashtag = inputs.hashtag()
    b = input("Do you want to enter date constraint? Y/N? ")
    from_date = inputs.from_date(b)
    to_date = inputs.to_date(b)
    csvFile = open('../Dataset/data.csv', 'w')
    csvWriter = csv.writer(csvFile)
    analyse_data.analysis(extract_data.authorize(), hashtag, from_date, to_date, csvWriter)
    
