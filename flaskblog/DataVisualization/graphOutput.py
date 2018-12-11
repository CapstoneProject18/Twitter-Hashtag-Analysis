import matplotlib.pyplot as plt
import pandas as pd
from flaskblog.FileLocations import file_locations


class GenerateGraph:

    def __init__(self):
        pass

    def num_hashtags(self, d, plt):
        fig = plt.figure()
        plt.bar(d.count()['tweets'].index.values, d.count()['tweets'].values)
        plt.xlabel("Date")
        plt.ylabel("Number of Hashtags")
        plt.title("Datewise Hashtag usages")
        plt.xticks(rotation=90)
        # plt.show()
        fig.savefig(file_locations.numofhashtags)


    def num_likes_retweets(self, d, plt):
        fig = plt.figure()
        likes = d['likes'].sum()
        retweet = d['retweet'].sum()
        plt.plot(likes.index.values, likes.values, color='g', label="Likes")
        plt.plot(retweet.index.values, retweet.values, color='b', label="Retweets")
        plt.xlabel("Date")
        plt.ylabel("Number of likes/retweets")
        plt.title("Datewise Hashtag usages")
        plt.legend(shadow=True, fontsize='x-large')
        plt.xticks(rotation=90)
        # plt.show()
        fig.savefig(file_locations.numoflikes)

    def top_hashtags(self, df, plt):
        fig = plt.figure()
        grouped = df.groupby('username').count().reset_index()
        people = (grouped.sort_values('tweets', ascending=False)).head(10)
        usernames = people['username'].str.extract(r'\'(.*)\'').values
        num_hashtag_by_user = people['tweets'].values
        x = [item for sublist in usernames for item in sublist]
        plt.bar(x, num_hashtag_by_user)
        plt.xlabel("User IDs")
        plt.ylabel("Number of Hashtags")
        plt.title("Hashtag Usages by top 10 users")
        plt.xticks(rotation=90)
        # plt.show()
        fig.savefig(file_locations.toptenusers)


if __name__ == '__main__':

    graph = GenerateGraph()
    df = pd.read_csv(file_locations.dataset,
                     names=['created_at', 'tweets', 'username', 'likes', 'retweet', 'coordinates'])
    d = df.groupby(df["created_at"].str[0:10])
    graph.num_hashtags(d, plt)
    graph.num_likes_retweets(d, plt)
    graph.top_hashtags(df, plt)
