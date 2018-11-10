import pandas as pd
import analyse


class ShowOutput:

    def __init__(self):
        pass

    def print_output(self):
        df = pd.read_csv("../Dataset/data.csv", names=['created_at', 'tweets', 'username'])

        print("\n\n")
        print("Number of tweets containing given hashtag are: " + str(len(df.index)))
        grouped = df.groupby('username').count().reset_index()
        print("\nTop 10 users influencing this hashtag are:\n")
        print((grouped.sort_values('tweets', ascending=False)).head(10))


if __name__ == '__main__':

    show_output = ShowOutput()
    show_output.print_output()
