import pandas as pd
from flaskblog.FileLocations import file_locations


class ShowOutput:

    def __init__(self):
        pass

    def print_output(self, df):
        grouped = df.groupby('username').count().reset_index()

        total = str(len(df.index))
        people = (grouped.sort_values('tweets', ascending=False)).head(10)

        return total, people


if __name__ == '__main__':

    show_output = ShowOutput()
    df = pd.read_csv(file_locations.dataset, names=['created_at', 'tweets', 'username', 'likes', 'retweet',
                                                    'coordinates'])
    total, people = show_output.print_output(df)
    print(total)
    print(people)
