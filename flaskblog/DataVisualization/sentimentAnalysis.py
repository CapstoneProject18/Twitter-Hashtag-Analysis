from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd
from flaskblog.FileLocations import file_locations


class SentimentAnalysis:

    def __init__(self):
        self.positive, self.negative, self.neutral, self.polarity, self.noOfSearchTerms = 0, 0, 0, 0, 0

    def percentage(self, part, whole):
        return 100 * float(part)/float(whole)

    def polarity_analysis(self, df):
        for tweet in df["tweets"]:
            # print(tweet.split("'")[1])
            tweet_text = tweet.split("'")[1]
            analysis = TextBlob(tweet_text)
            self.polarity += analysis.sentiment.polarity
            if analysis.sentiment.polarity == 0:
                self.neutral += 1
            elif analysis.sentiment.polarity < 0.00:
                self.negative += 1
            elif analysis.sentiment.polarity > 0.00:
                self.positive += 1
            self.noOfSearchTerms = self.noOfSearchTerms + 1

        self.positive = self.percentage(self.positive, self.noOfSearchTerms)
        self.negative = self.percentage(self.negative, self.noOfSearchTerms)
        self.neutral = self.percentage(self.neutral, self.noOfSearchTerms)
        self.polarity = self.percentage(self.polarity, self.noOfSearchTerms)
        self.positive = format(self.positive, '.2f')
        self.neutral = format(self.neutral, '.2f')
        self.negative = format(self.negative, '.2f')

        if self.polarity == 0:
            return "Neutral"
        elif self.polarity < 0.00:
            return "Negative"
        elif self.polarity > 0.00:
            return "Positive"

    def show_graph(self):
        fig = plt.figure()
        labels = ['Postive [' + str(self.positive) + '%]', 'Neutral [' + str(self.neutral) + '%]',
                  'Negative [' + str(self.negative) + '%]']
        sizes = [self.positive, self.neutral, self.negative]
        colors = ['yellowgreen', 'gold', 'red']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)

        plt.legend(patches, labels, loc="best")
        plt.title('Sentiment Analysis of twitter texts')
        plt.axis('equal')
        plt.tight_layout()
        # plt.show()
        fig.savefig(file_locations.sentigraph)


    def f(self, x):
        return pd.Series(dict(Likes=x['likes'].sum(),
                              Retwwets=x['retweet'].sum(),
                              NumHashtags=x['num'].sum(),
                              Tweets="{%s}" % ', '.join(str(x['tweets']))))

    def ten_hashtags_polarity(self, df):
        tweets = df['tweets'].head(10).str.extract(r'\'(.*)\'').values
        x = [item for sublist in tweets for item in sublist]
        data = []
        for item in x:
            p = TextBlob(str(item)).sentiment.polarity
            if p == 0:
                data.extend([[item, "Neutral"]])
            elif p < 0.00:
                data.extend([[item, "Negative"]])
            elif p > 0.00:
                data.extend([[item, "Positive"]])
        return pd.DataFrame(data, columns=['Tweets', 'Sentiment'])


if __name__ == '__main__':

    df = pd.read_csv(file_locations.dataset,
                     names=['created_at', 'tweets', 'username', 'likes', 'retweet', 'coordinates'])
    sentimentAnalysis = SentimentAnalysis()
    print("Overall Polarity: " + sentimentAnalysis.polarity_analysis(df))
    sentimentAnalysis.show_graph()
    print(sentimentAnalysis.ten_hashtags_polarity(df))
