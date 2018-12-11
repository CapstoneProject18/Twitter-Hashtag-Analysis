import tweepy
from flaskblog.DataExtraction import twitter_credentials


class ExtractData:

    def __init__(self):
        pass

    def authorize(self):
        auth = tweepy.OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return tweepy.API(auth, wait_on_rate_limit=True)

    def extract_save(self, api, keyword):
        for tweet in tweepy.Cursor(api.search, q=keyword, lang="en", since="1").items():
            print(tweet)


if __name__ == '__main__':
    extract_data = ExtractData()
    extract_data.extract_save(extract_data.authorize(), "camel")
